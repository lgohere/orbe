"""
Finance module signals for auto-creating assistance cases.

This module handles the automatic workflow transition:
DonationRequest (approved) → AssistanceCase (awaiting_transfer)
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import DonationRequest


@receiver(post_save, sender=DonationRequest)
def create_assistance_case_on_approval(sender, instance, created, **kwargs):
    """
    Auto-create AssistanceCase when DonationRequest is approved.

    Workflow:
    1. Admin approves DonationRequest → status = 'approved'
    2. Signal triggers → Creates linked AssistanceCase
    3. AssistanceCase starts in 'awaiting_transfer' status
    4. Admin must confirm transfer to member (upload PIX proof)
    5. Member confirms application to beneficiary (upload photos)
    6. Admin validates and completes case

    Args:
        sender: DonationRequest model class
        instance: The DonationRequest that was saved
        created: Boolean, True if new instance
        **kwargs: Additional keyword arguments
    """
    if instance.status != 'approved':
        return

    # Import here to avoid circular dependency
    from assistance.models import AssistanceCase

    try:
        instance.assistance_case
        case_exists = True
    except AssistanceCase.DoesNotExist:
        case_exists = False

    # Only trigger if status changed to 'approved' and no case exists yet
    if not case_exists:
        # Create linked assistance case
        AssistanceCase.objects.create(
            # Link to the donation request
            donation_request=instance,

            # Copy donor information
            title=f"Doação para {instance.recipient_name}",
            public_description=instance.recipient_description,
            internal_description=f"""
Solicitação de doação aprovada.

**Beneficiário**: {instance.recipient_name}
**Valor**: R$ {instance.amount}
**Urgência**: {instance.get_urgency_level_display()}
**Motivo**: {instance.reason}

**Solicitado por**: {instance.requested_by.get_full_name() or instance.requested_by.email}
**Aprovado por**: {instance.reviewed_by.get_full_name() or instance.reviewed_by.email}
**Data de aprovação**: {instance.approved_at.strftime('%d/%m/%Y %H:%M')}
            """.strip(),

            # Financial
            total_value=instance.amount,

            # Status starts as awaiting_bank_info
            # Member must first provide beneficiary bank information
            status='awaiting_bank_info',

            # Track creator (member who requested)
            created_by=instance.requested_by,

            # Track approver (admin who approved request)
            reviewed_by=instance.reviewed_by,

            # Set approval timestamp
            approved_at=instance.approved_at or timezone.now(),
        )

        print(f"[SIGNAL] Created AssistanceCase for approved DonationRequest #{instance.id}")
