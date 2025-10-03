from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import MembershipFee, DonationRequest, VoluntaryDonation


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


@admin.register(VoluntaryDonation)
class VoluntaryDonationAdmin(admin.ModelAdmin):
    """Admin configuration for Voluntary Donations (TO ORBE)"""
    list_display = [
        'id',
        'donor_display',
        'amount_display',
        'is_anonymous',
        'verified_badge',
        'donated_at',
    ]
    list_filter = [
        'is_anonymous',
        'donated_at',
        ('verified_by', admin.EmptyFieldListFilter),
    ]
    search_fields = [
        'donor__email',
        'donor__first_name',
        'donor__last_name',
        'message',
    ]
    readonly_fields = [
        'donated_at',
        'display_name',
    ]
    fieldsets = (
        ('Donor Information', {
            'fields': ('donor', 'is_anonymous', 'display_name')
        }),
        ('Donation Details', {
            'fields': ('amount', 'message', 'payment_proof')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at')
        }),
        ('Timestamps', {
            'fields': ('donated_at',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'donated_at'
    ordering = ['-donated_at']
    actions = ['verify_donations']

    @admin.display(description='Donor')
    def donor_display(self, obj):
        if obj.is_anonymous or not obj.donor:
            return format_html('<em style="color: gray;">Anônimo</em>')
        return f"{obj.donor.first_name} {obj.donor.last_name}".strip() or obj.donor.email

    @admin.display(description='Amount')
    def amount_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">R$ {:.2f}</span>',
            obj.amount
        )

    @admin.display(description='Verified')
    def verified_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">✓ Verificado</span>'
            )
        return format_html(
            '<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">Pendente</span>'
        )

    @admin.action(description='Mark as verified')
    def verify_donations(self, request, queryset):
        updated = queryset.filter(verified_by__isnull=True).update(
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} donations verified.')


@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    """Admin configuration for Donation Requests (FOR THIRD PARTIES)"""
    list_display = [
        'id',
        'requester_name',
        'recipient_name',
        'amount_display',
        'urgency_badge',
        'status_badge',
        'created_at',
        'reviewed_by_name',
    ]
    list_filter = [
        'status',
        'urgency_level',
        'created_at',
        'approved_at',
    ]
    search_fields = [
        'requested_by__email',
        'requested_by__first_name',
        'requested_by__last_name',
        'recipient_name',
        'reason',
    ]
    readonly_fields = [
        'created_at',
        'approved_at',
        'updated_at',
        'can_edit',
        'can_delete',
    ]
    fieldsets = (
        ('Requester Information', {
            'fields': ('requested_by',)
        }),
        ('Beneficiary Details', {
            'fields': ('recipient_name', 'recipient_description', 'amount', 'reason', 'urgency_level')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'approved_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['approve_requests', 'reject_requests']

    @admin.display(description='Requester')
    def requester_name(self, obj):
        return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip() or obj.requested_by.email

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

    @admin.display(description='Urgency')
    def urgency_badge(self, obj):
        colors = {
            'low': 'gray',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred',
        }
        color = colors.get(obj.urgency_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_urgency_level_display()
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending_approval': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.action(description='Approve selected requests')
    def approve_requests(self, request, queryset):
        # TODO: Trigger signal to create AssistanceCase
        updated = queryset.filter(status='pending_approval').update(
            status='approved',
            reviewed_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests approved. AssistanceCase will be created automatically.')

    @admin.action(description='Reject selected requests')
    def reject_requests(self, request, queryset):
        count = 0
        for obj in queryset.filter(status='pending_approval'):
            obj.status = 'rejected'
            obj.reviewed_by = request.user
            obj.rejection_reason = 'Rejected via bulk action'  # Could prompt for reason
            obj.save()
            count += 1
        self.message_user(request, f'{count} requests rejected.')
