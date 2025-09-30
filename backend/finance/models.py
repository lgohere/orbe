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
    Represents voluntary donations to ORBE.
    Can be anonymous (user=null) and with optional amount.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations',
        verbose_name=_('User'),
        help_text=_('Anonymous donations allowed (null)')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount'),
        help_text=_('Donation amount (optional, can be null)')
    )
    message = models.TextField(
        blank=True,
        verbose_name=_('Message'),
        help_text=_('Optional message from donor')
    )
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name=_('Anonymous Donation'),
        help_text=_('Hide donor name in public feed')
    )
    donated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Donated At')
    )

    class Meta:
        verbose_name = _('Donation')
        verbose_name_plural = _('Donations')
        ordering = ['-donated_at']
        indexes = [
            models.Index(fields=['user', 'donated_at']),
            models.Index(fields=['donated_at']),
        ]

    def __str__(self):
        donor = self.user.email if self.user else 'Anonymous'
        amount_str = f"R${self.amount:.2f}" if self.amount else 'No amount'
        return f"{donor} - {amount_str} - {self.donated_at.strftime('%Y-%m-%d')}"

    @property
    def donor_display_name(self):
        """Get display name for donor (respects anonymity)"""
        if self.is_anonymous:
            return _('Anonymous Donor')
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email
        return _('Anonymous Donor')
