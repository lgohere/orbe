from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from users.models import User


class MembershipFee(models.Model):
    """
    Represents monthly membership fees for ORBE members.
    R$60.00/month with customizable due dates (1-28 of each month).
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='membership_fees',
        verbose_name=_('User')
    )
    competency_month = models.DateField(
        verbose_name=_('Competency Month'),
        help_text=_('Month/Year this fee is for (e.g., 2025-01-01)')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=60.00,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount'),
        help_text=_('Monthly fee amount (default: R$60.00)')
    )
    due_date = models.DateField(
        verbose_name=_('Due Date'),
        help_text=_('Calculated from user.profile.membership_due_day')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Paid At')
    )
    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reminder Sent At'),
        help_text=_('Timestamp when D-0 reminder was sent')
    )
    overdue_reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Overdue Reminder Sent At'),
        help_text=_('Timestamp when D+3 overdue reminder was sent')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes'),
        help_text=_('Internal notes about this fee')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Membership Fee')
        verbose_name_plural = _('Membership Fees')
        unique_together = ('user', 'competency_month')
        ordering = ['-competency_month', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['competency_month']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.competency_month.strftime('%Y-%m')} - {self.get_status_display()}"

    @property
    def is_overdue(self):
        """Check if this fee is overdue"""
        from django.utils import timezone
        return self.status == 'pending' and self.due_date < timezone.now().date()

    @property
    def days_overdue(self):
        """Calculate how many days overdue this fee is"""
        from django.utils import timezone
        if not self.is_overdue:
            return 0
        delta = timezone.now().date() - self.due_date
        return delta.days


# ==========================================
# DONATION MODELS (Two Types)
# ==========================================

class VoluntaryDonation(models.Model):
    """
    Represents a VOLUNTARY donation made BY a member/external person TO ORBE.

    This is ADDITIONAL to monthly membership fees (R$60).
    Members donate spontaneously to support ORBE's mission.
    Can be anonymous or public (appears in feed for transparency).

    Example: "I want to contribute R$100 extra this month to help ORBE"
    """

    # Donor (can be null for anonymous donations)
    donor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voluntary_donations',
        verbose_name=_('Doador'),
        help_text=_('Membro que fez a doação (nulo se anônimo)')
    )

    # Donation Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Valor'),
        help_text=_('Valor doado (R$)')
    )

    message = models.TextField(
        blank=True,
        verbose_name=_('Mensagem'),
        help_text=_('Mensagem opcional do doador')
    )

    is_anonymous = models.BooleanField(
        default=False,
        verbose_name=_('Doação Anônima'),
        help_text=_('Se marcado, o nome do doador não aparecerá no feed')
    )

    # Payment Proof (optional for verification)
    payment_proof = models.FileField(
        upload_to='voluntary_donations/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_('Comprovante de Pagamento'),
        help_text=_('Comprovante de PIX/transferência (opcional)')
    )

    # Timestamps
    donated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data da Doação')
    )

    # Admin verification (optional)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_voluntary_donations',
        verbose_name=_('Verificado por'),
        help_text=_('Admin que confirmou o recebimento')
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Verificado em')
    )

    class Meta:
        verbose_name = _('Doação Espontânea')
        verbose_name_plural = _('Doações Espontâneas')
        ordering = ['-donated_at']
        indexes = [
            models.Index(fields=['-donated_at']),
            models.Index(fields=['donor', '-donated_at']),
        ]

    def __str__(self):
        donor_name = self.donor.get_full_name() if self.donor and not self.is_anonymous else 'Anônimo'
        return f"{donor_name} - R${self.amount:.2f} - {self.donated_at.strftime('%d/%m/%Y')}"

    @property
    def display_name(self):
        """Get display name for feed (respects anonymity)"""
        if self.is_anonymous or not self.donor:
            return 'Doador Anônimo'
        return self.donor.get_full_name()

    @property
    def is_verified(self):
        """Check if donation was verified by admin"""
        return self.verified_by is not None


class DonationRequest(models.Model):
    """
    Represents a REQUEST for ORBE to donate TO someone in need.

    Workflow:
    1. Member submits request → 'pending_approval'
    2. Admin approves → 'approved' (creates AssistanceCase automatically)
    3. Admin rejects → 'rejected'

    Once approved, the actual donation execution is tracked via AssistanceCase.

    Example: "I know a family that needs groceries - can ORBE help them?"
    """
    STATUS_CHOICES = [
        ('pending_approval', _('Pendente de Aprovação')),
        ('approved', _('Aprovado')),
        ('rejected', _('Rejeitado')),
    ]

    # Requester (Member who knows about the need)
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='donation_requests',
        verbose_name=_('Solicitado por'),
        help_text=_('Membro que solicitou a doação')
    )

    # Beneficiary Information
    recipient_name = models.CharField(
        max_length=200,
        verbose_name=_('Nome do Beneficiário'),
        help_text=_('Nome da pessoa/família que receberá a doação (pode ser anônimo na publicação)')
    )

    recipient_description = models.TextField(
        verbose_name=_('Descrição do Beneficiário'),
        help_text=_('Informações sobre o beneficiário e sua situação')
    )

    # Request Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Valor Estimado'),
        help_text=_('Valor aproximado necessário (R$)')
    )

    reason = models.TextField(
        verbose_name=_('Motivo da Necessidade'),
        help_text=_('Por que essa doação é necessária (ex: cesta básica, remédios, conta de luz)')
    )

    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Baixa')),
            ('medium', _('Média')),
            ('high', _('Alta')),
            ('critical', _('Crítica'))
        ],
        default='medium',
        verbose_name=_('Nível de Urgência')
    )

    # Status & Workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_approval',
        verbose_name=_('Status'),
        db_index=True
    )

    # Admin Review
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_donation_requests',
        verbose_name=_('Revisado por'),
        help_text=_('Admin que aprovou/rejeitou')
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_('Motivo da Rejeição'),
        help_text=_('Explicação do admin sobre a rejeição')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Criado em')
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Aprovado em')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Atualizado em')
    )

    class Meta:
        verbose_name = _('Solicitação de Doação')
        verbose_name_plural = _('Solicitações de Doação')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['urgency_level', 'status']),
        ]

    def __str__(self):
        return f"{self.requested_by.first_name} → {self.recipient_name} - R${self.amount:.2f}"

    @property
    def can_edit(self):
        """Only pending requests can be edited"""
        return self.status == 'pending_approval'

    @property
    def can_delete(self):
        """Only pending requests can be deleted"""
        return self.status == 'pending_approval'

    @property
    def is_approved(self):
        """Check if request was approved"""
        return self.status == 'approved'

    @property
    def is_rejected(self):
        """Check if request was rejected"""
        return self.status == 'rejected'

    @property
    def is_pending(self):
        """Check if request is pending review"""
        return self.status == 'pending_approval'
