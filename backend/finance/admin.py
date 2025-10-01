from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import MembershipFee, Donation


@admin.register(MembershipFee)
class MembershipFeeAdmin(admin.ModelAdmin):
    """Admin configuration for MembershipFee model"""
    list_display = [
        'id',
        'user_email',
        'user_name',
        'competency_month',
        'amount',
        'due_date',
        'status_badge',
        'days_overdue_display',
        'paid_at',
        'created_at',
    ]
    list_filter = [
        'status',
        'competency_month',
        'due_date',
        'created_at',
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'notes',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'is_overdue',
        'days_overdue',
    ]
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Fee Details', {
            'fields': ('competency_month', 'amount', 'due_date', 'status')
        }),
        ('Payment Information', {
            'fields': ('paid_at',)
        }),
        ('Reminders', {
            'fields': ('reminder_sent_at', 'overdue_reminder_sent_at')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_overdue', 'days_overdue')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'competency_month'
    ordering = ['-competency_month', '-created_at']
    actions = ['mark_as_paid', 'mark_as_overdue']

    @admin.display(description='User Email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='User Name')
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or '-'

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'overdue': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.display(description='Days Overdue')
    def days_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">{} days</span>',
                obj.days_overdue
            )
        return '-'

    @admin.action(description='Mark selected fees as paid')
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid', paid_at=timezone.now())
        self.message_user(request, f'{updated} fees marked as paid.')

    @admin.action(description='Mark selected fees as overdue')
    def mark_as_overdue(self, request, queryset):
        updated = queryset.update(status='overdue')
        self.message_user(request, f'{updated} fees marked as overdue.')


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """Admin configuration for Donation Request model"""
    list_display = [
        'id',
        'requester_name',
        'recipient',
        'amount_display',
        'status_badge',
        'created_at',
        'reviewed_by_name',
    ]
    list_filter = [
        'status',
        'created_at',
        'approved_at',
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'recipient',
        'reason',
    ]
    readonly_fields = [
        'created_at',
        'approved_at',
        'completed_at',
        'can_edit',
        'can_delete',
    ]
    fieldsets = (
        ('Requester Information', {
            'fields': ('user',)
        }),
        ('Request Details', {
            'fields': ('recipient', 'amount', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'rejection_reason')
        }),
        ('Proof', {
            'fields': ('proof_document',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'approved_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['approve_requests', 'mark_as_completed']

    @admin.display(description='Requester')
    def requester_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return '-'

    @admin.display(description='Reviewed By')
    def reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.email
        return '-'

    @admin.display(description='Amount')
    def amount_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">R$ {:.2f}</span>',
            obj.amount
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending_approval': 'orange',
            'approved': 'blue',
            'rejected': 'red',
            'proof_attached': 'purple',
            'completed': 'green',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.action(description='Approve selected requests')
    def approve_requests(self, request, queryset):
        updated = queryset.filter(status='pending_approval').update(
            status='approved',
            reviewed_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests approved.')

    @admin.action(description='Mark selected requests as completed')
    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status__in=['approved', 'proof_attached']).update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests marked as completed.')
