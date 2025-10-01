from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
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


class Donation(models.Model):
    """
    Represents donation requests from members.
    Members request donations for specific recipients/reasons.
    Admin approves, attaches proof, and marks as completed.
    """
    STATUS_CHOICES = [
        ('pending_approval', _('Pendente de Aprovação')),
        ('approved', _('Aprovado')),
        ('rejected', _('Rejeitado')),
        ('proof_attached', _('Comprovante Anexado')),
        ('completed', _('Concluído')),
    ]

    # Requester (Member)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='donations',
        verbose_name=_('Requester'),
        help_text=_('Member who requested the donation')
    )

    # Donation Details
    recipient = models.CharField(
        max_length=200,
        verbose_name=_('Recipient'),
        help_text=_('Who will receive the donation')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount'),
        help_text=_('Requested donation amount')
    )
    reason = models.TextField(
        verbose_name=_('Reason'),
        help_text=_('Why this donation is needed (e.g., groceries, rent, medical)')
    )

    # Workflow Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_approval',
        verbose_name=_('Status')
    )

    # Admin Actions
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_donations',
        verbose_name=_('Reviewed By'),
        help_text=_('Admin/Board member who reviewed')
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_('Rejection Reason'),
        help_text=_('Why this donation was rejected')
    )
    proof_document = models.FileField(
        upload_to='donation_proofs/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_('Proof Document'),
        help_text=_('Receipt/proof of donation (PDF)')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approved At')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )

    class Meta:
        verbose_name = _('Donation Request')
        verbose_name_plural = _('Donation Requests')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.recipient} - R${self.amount:.2f} - {self.get_status_display()}"

    @property
    def can_edit(self):
        """Check if donation request can be edited (only pending)"""
        return self.status == 'pending_approval'

    @property
    def can_delete(self):
        """Check if donation request can be deleted (only pending)"""
        return self.status == 'pending_approval'
