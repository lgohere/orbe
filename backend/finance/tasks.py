"""
Celery tasks for finance module
Handles automated membership fee reminders and financial operations
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta
import logging
import requests

from .models import MembershipFee

logger = logging.getLogger(__name__)


@shared_task(name='finance.send_membership_reminders')
def send_membership_reminders():
    """
    Send D-0 reminders for membership fees due today.
    Runs daily at 9:00 AM via Celery Beat.
    """
    today = date.today()
    logger.info(f"Running D-0 membership reminders for {today}")

    # Find fees that are due today and haven't been reminded yet
    fees_due_today = MembershipFee.objects.filter(
        due_date=today,
        status='pending',
        reminder_sent_at__isnull=True
    ).select_related('user', 'user__profile')

    reminder_count = 0

    for fee in fees_due_today:
        try:
            # Send reminder via n8n webhook
            success = _send_reminder_webhook(
                user=fee.user,
                fee=fee,
                reminder_type='due_today'
            )

            if success:
                # Update reminder timestamp
                fee.reminder_sent_at = timezone.now()
                fee.save(update_fields=['reminder_sent_at'])
                reminder_count += 1
                logger.info(f"Sent D-0 reminder to {fee.user.email} for {fee.competency_month}")
            else:
                logger.error(f"Failed to send D-0 reminder to {fee.user.email}")

        except Exception as e:
            logger.error(f"Error sending D-0 reminder to {fee.user.email}: {str(e)}")

    logger.info(f"Sent {reminder_count} D-0 reminders")
    return {
        'reminder_type': 'D-0',
        'date': today.isoformat(),
        'reminders_sent': reminder_count
    }


@shared_task(name='finance.send_overdue_reminders')
def send_overdue_reminders():
    """
    Send D+3 reminders for membership fees that are 3 days overdue.
    Runs daily at 9:00 AM via Celery Beat.
    """
    today = date.today()
    three_days_ago = today - timedelta(days=3)
    logger.info(f"Running D+3 overdue reminders for fees due on {three_days_ago}")

    # Find fees that are 3 days overdue and haven't received overdue reminder
    overdue_fees = MembershipFee.objects.filter(
        due_date=three_days_ago,
        status__in=['pending', 'overdue'],
        overdue_reminder_sent_at__isnull=True
    ).select_related('user', 'user__profile')

    reminder_count = 0

    for fee in overdue_fees:
        try:
            # Mark as overdue if still pending
            if fee.status == 'pending':
                fee.status = 'overdue'

            # Send overdue reminder via n8n webhook
            success = _send_reminder_webhook(
                user=fee.user,
                fee=fee,
                reminder_type='overdue'
            )

            if success:
                # Update overdue reminder timestamp
                fee.overdue_reminder_sent_at = timezone.now()
                fee.save(update_fields=['status', 'overdue_reminder_sent_at'])
                reminder_count += 1
                logger.info(f"Sent D+3 overdue reminder to {fee.user.email} for {fee.competency_month}")
            else:
                logger.error(f"Failed to send D+3 overdue reminder to {fee.user.email}")

        except Exception as e:
            logger.error(f"Error sending D+3 overdue reminder to {fee.user.email}: {str(e)}")

    logger.info(f"Sent {reminder_count} D+3 overdue reminders")
    return {
        'reminder_type': 'D+3',
        'date': today.isoformat(),
        'reminders_sent': reminder_count
    }


@shared_task(name='finance.update_overdue_status')
def update_overdue_status():
    """
    Update status of pending fees that are past due date to 'overdue'.
    Runs daily at midnight via Celery Beat.
    """
    today = date.today()
    logger.info(f"Updating overdue status for fees past {today}")

    # Find pending fees with due date before today
    updated_count = MembershipFee.objects.filter(
        due_date__lt=today,
        status='pending'
    ).update(status='overdue')

    logger.info(f"Updated {updated_count} fees to overdue status")
    return {
        'date': today.isoformat(),
        'updated_count': updated_count
    }


@shared_task(name='finance.generate_monthly_fees')
def generate_monthly_fees(year=None, month=None):
    """
    Generate membership fees for all active members for a specific month.
    Args:
        year: Year to generate fees for (default: current year)
        month: Month to generate fees for (default: current month)
    """
    from users.models import User
    from calendar import monthrange

    today = date.today()
    year = year or today.year
    month = month or today.month

    logger.info(f"Generating membership fees for {year}-{month:02d}")

    # Get all members (exclude super admins)
    active_members = User.objects.filter(
        is_active=True,
        profile__is_onboarding_completed=True
    ).exclude(
        role='SUPER_ADMIN'
    ).select_related('profile')

    competency_month = date(year, month, 1)
    created_count = 0
    skipped_count = 0

    for user in active_members:
        try:
            # Calculate due date based on user's preferred day
            due_day = user.profile.membership_due_day
            _, last_day = monthrange(year, month)
            # Ensure due_day doesn't exceed month's last day
            due_day = min(due_day, last_day)
            due_date = date(year, month, due_day)

            # Create fee if it doesn't exist
            fee, created = MembershipFee.objects.get_or_create(
                user=user,
                competency_month=competency_month,
                defaults={
                    'amount': 60.00,
                    'due_date': due_date,
                    'status': 'pending'
                }
            )

            if created:
                created_count += 1
                logger.info(f"Created fee for {user.email} - {competency_month}")
            else:
                skipped_count += 1

        except Exception as e:
            logger.error(f"Error creating fee for {user.email}: {str(e)}")

    logger.info(f"Fee generation complete: {created_count} created, {skipped_count} skipped")
    return {
        'competency_month': competency_month.isoformat(),
        'created_count': created_count,
        'skipped_count': skipped_count
    }


def _send_reminder_webhook(user, fee, reminder_type):
    """
    Internal helper to send reminder via n8n webhook.
    Args:
        user: User object
        fee: MembershipFee object
        reminder_type: 'due_today' or 'overdue'
    Returns:
        bool: True if successful, False otherwise
    """
    webhook_url = "https://n8n.texts.com.br/webhook-test/orbe_membership_reminder"

    payload = {
        "reminder_type": reminder_type,
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "language": user.profile.language_preference,
        "competency_month": fee.competency_month.strftime('%Y-%m'),
        "due_date": fee.due_date.isoformat(),
        "amount": float(fee.amount),
        "days_overdue": fee.days_overdue if reminder_type == 'overdue' else 0,
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Webhook error for {user.email}: {str(e)}")
        return False