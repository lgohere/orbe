"""
Signals for automatic timeline event tracking.

Every significant action on AssistanceCase creates a timeline event automatically.
This ensures complete audit trail without manual logging in views.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import AssistanceCase, Attachment, CaseTimeline


def _cleanup_timeline_after_rollback(case, old_status, new_status):
    """
    Remove timeline events that are no longer valid after status rollback.

    Business Rule: "O histórico deve espelhar exatamente a situação ATUAL do estado"

    When status rolls back, remove all events that happened AFTER the current state:
    - If rollback to awaiting_transfer: remove transfer_confirmed, member_proof_submitted, attachment uploads
    - If rollback to awaiting_member_proof: remove member_proof_submitted, photo evidence uploads

    This ensures timeline only shows events relevant to the current case state.
    """

    # Define which events to remove based on rollback transition
    events_to_remove = []

    if new_status == 'awaiting_transfer':
        # Rolled back to awaiting_transfer - remove everything after bank_info_submitted
        events_to_remove = [
            'transfer_confirmed',
            'member_proof_submitted',
            'attachment_uploaded',  # Remove all attachment uploads (will be re-uploaded)
            'attachment_deleted',  # Remove deletion events (attachments don't exist in current state)
            'status_rollback',  # Remove previous rollback events
            'completed',
            'rejected'
        ]
    elif new_status == 'awaiting_member_proof':
        # Rolled back to awaiting_member_proof - remove only member proof events
        events_to_remove = [
            'member_proof_submitted',
            'attachment_deleted',  # Remove deletion events
            'status_rollback',
            'completed',
            'rejected'
        ]
        # Also remove photo_evidence attachments specifically
        case.timeline_events.filter(
            event_type='attachment_uploaded',
            metadata__attachment_type='photo_evidence'
        ).delete()

    # Delete events that are no longer valid
    case.timeline_events.filter(event_type__in=events_to_remove).delete()


@receiver(post_save, sender=AssistanceCase)
def log_case_creation(sender, instance, created, **kwargs):
    """Log case creation event"""
    if created:
        CaseTimeline.log_event(
            case=instance,
            event_type='case_created',
            user=instance.created_by,
            description=f'Caso criado: {instance.title}',
            metadata={
                'status': instance.status,
                'total_value': str(instance.total_value)
            }
        )


@receiver(pre_save, sender=AssistanceCase)
def track_status_changes(sender, instance, **kwargs):
    """
    Track all status changes and create appropriate timeline events.
    Uses pre_save to compare old vs new status.
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = AssistanceCase.objects.get(pk=instance.pk)
            old_status = old_instance.status
            new_status = instance.status

            # Status changed - log it after save
            if old_status != new_status:
                # Store the change for post_save signal
                instance._status_changed = {
                    'old_status': old_status,
                    'new_status': new_status
                }
        except AssistanceCase.DoesNotExist:
            pass


@receiver(post_save, sender=AssistanceCase)
def log_status_change_events(sender, instance, created, **kwargs):
    """
    Log specific timeline events based on status transitions.
    Called after save to ensure all data is persisted.
    """
    if created:
        return  # Already logged in log_case_creation

    # Check if status changed (set by pre_save signal)
    if hasattr(instance, '_status_changed'):
        change_data = instance._status_changed
        old_status = change_data['old_status']
        new_status = change_data['new_status']

        # Map status transitions to timeline events
        status_event_map = {
            ('draft', 'pending_approval'): {
                'event_type': 'submitted_for_approval',
                'description': 'Caso enviado para aprovação do admin',
                'user': instance.created_by
            },
            ('pending_approval', 'awaiting_bank_info'): {
                'event_type': 'approved',
                'description': f'Caso aprovado por {instance.reviewed_by.get_full_name() if instance.reviewed_by else "Admin"}',
                'user': instance.reviewed_by
            },
            ('pending_approval', 'rejected'): {
                'event_type': 'rejected',
                'description': f'Caso rejeitado: {instance.rejection_reason}',
                'user': instance.reviewed_by,
                'metadata': {'rejection_reason': instance.rejection_reason}
            },
            ('awaiting_bank_info', 'awaiting_transfer'): {
                'event_type': 'bank_info_submitted',
                'description': 'Dados bancários do beneficiário informados',
                'user': instance.created_by,
                'metadata': {
                    'beneficiary_name': instance.beneficiary_name,
                    'beneficiary_bank': instance.beneficiary_bank,
                    'beneficiary_pix_key': instance.beneficiary_pix_key
                }
            },
            ('awaiting_transfer', 'awaiting_member_proof'): {
                'event_type': 'transfer_confirmed',
                'description': 'Admin confirmou transferência para o membro',
                'user': instance.reviewed_by
            },
            ('awaiting_member_proof', 'pending_validation'): {
                'event_type': 'member_proof_submitted',
                'description': 'Membro enviou comprovantes da aplicação ao beneficiário',
                'user': instance.created_by
            },
            ('pending_validation', 'completed'): {
                'event_type': 'completed',
                'description': f'Caso concluído e validado por {instance.reviewed_by.get_full_name() if instance.reviewed_by else "Admin"}',
                'user': instance.reviewed_by
            },
            ('pending_validation', 'rejected'): {
                'event_type': 'rejected',
                'description': f'Comprovantes rejeitados: {instance.rejection_reason}',
                'user': instance.reviewed_by,
                'metadata': {'rejection_reason': instance.rejection_reason}
            },
            # ROLLBACK TRANSITIONS (triggered by attachment deletion)
            ('pending_validation', 'awaiting_transfer'): {
                'event_type': 'status_rollback',
                'description': 'Status revertido para "Aguardando Transferência" devido à remoção de anexos críticos',
                'user': None,  # System action
                'metadata': {'rollback_reason': 'payment_proof_deleted'}
            },
            ('pending_validation', 'awaiting_member_proof'): {
                'event_type': 'status_rollback',
                'description': 'Status revertido para "Aguardando Comprovante do Membro" devido à remoção de comprovantes',
                'user': None,  # System action
                'metadata': {'rollback_reason': 'photo_evidence_deleted'}
            },
            ('awaiting_member_proof', 'awaiting_transfer'): {
                'event_type': 'status_rollback',
                'description': 'Status revertido para "Aguardando Transferência" devido à remoção do comprovante de pagamento',
                'user': None,  # System action
                'metadata': {'rollback_reason': 'payment_proof_deleted'}
            },
        }

        # Get event config for this transition
        transition_key = (old_status, new_status)
        if transition_key in status_event_map:
            event_config = status_event_map[transition_key]
            CaseTimeline.log_event(
                case=instance,
                event_type=event_config['event_type'],
                user=event_config.get('user'),
                description=event_config['description'],
                metadata=event_config.get('metadata', {})
            )
        else:
            # Generic status change (fallback)
            CaseTimeline.log_event(
                case=instance,
                event_type='status_changed',
                description=f'Status alterado de "{old_status}" para "{new_status}"',
                metadata={
                    'old_status': old_status,
                    'new_status': new_status
                }
            )

        # Clean up temporary attribute
        delattr(instance, '_status_changed')


@receiver(post_save, sender=Attachment)
def log_attachment_upload(sender, instance, created, **kwargs):
    """
    Log when files are uploaded to a case.

    NOTE: Attachment events may be removed during rollback to keep timeline
    clean and reflecting only current state.
    """
    if created:
        CaseTimeline.log_event(
            case=instance.case,
            event_type='attachment_uploaded',
            user=instance.uploaded_by,
            description=f'Arquivo anexado: {instance.file_name}',
            metadata={
                'attachment_type': instance.attachment_type,
                'file_name': instance.file_name,
                'file_type': instance.file_type,
                'file_size': instance.file_size
            }
        )


@receiver(post_delete, sender=Attachment)
def revalidate_case_on_attachment_delete(sender, instance, **kwargs):
    """
    Automatically revalidate case status when attachments are deleted.

    This implements the critical business rule:
    "Quando os anexos são deletados o histórico deve também voltar aos estados anteriores"

    Examples:
    - Delete payment_proof from awaiting_member_proof → rollback to awaiting_transfer
    - Delete payment_proof from pending_validation → rollback to awaiting_transfer
    - Delete photo_evidence from pending_validation → rollback to awaiting_member_proof

    Timeline events are created automatically by the pre_save/post_save signals
    when revalidate_status() changes the case status.
    """
    case = instance.case
    attachment_type = instance.attachment_type
    deleted_by = instance.uploaded_by  # Track who originally uploaded the deleted file

    # Store old status before revalidation
    old_status = case.status

    # Trigger automatic status rollback
    status_changed = case.revalidate_status()

    if status_changed:
        # CRITICAL: Clean up timeline to reflect current state only
        # Remove events that are no longer valid after rollback
        _cleanup_timeline_after_rollback(case, old_status, case.status)
    # NO logging of deletion events - history should only show current state
