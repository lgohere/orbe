"""
Django admin configuration for assistance module.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import AssistanceCase, Attachment, CaseTimeline


class CaseTimelineInline(admin.TabularInline):
    """Inline admin for timeline events"""
    model = CaseTimeline
    extra = 0
    readonly_fields = ['event_type', 'description', 'user', 'metadata', 'created_at']
    fields = ['created_at', 'event_type', 'description', 'user', 'metadata']
    can_delete = False
    ordering = ['created_at']

    def has_add_permission(self, request, obj=None):
        """Prevent manual timeline entry creation"""
        return False


class AttachmentInline(admin.TabularInline):
    """Inline admin for attachments"""
    model = Attachment
    extra = 0
    readonly_fields = ['file_name', 'file_type', 'file_size', 'file_size_mb', 'uploaded_at', 'uploaded_by', 'file_preview', 'attachment_type']
    fields = ['file', 'attachment_type', 'file_preview', 'file_name', 'file_type', 'file_size_mb', 'uploaded_by', 'uploaded_at']
    can_delete = True

    def file_preview(self, obj):
        """Show file preview or icon"""
        if obj.pk and obj.file:
            if obj.is_image:
                return format_html(
                    '<a href="{}" target="_blank"><img src="{}" style="max-height: 50px; max-width: 100px;"/></a>',
                    obj.file.url,
                    obj.file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank">📄 {}</a>',
                    obj.file.url,
                    obj.file_name
                )
        return "-"
    file_preview.short_description = "Preview"


@admin.register(CaseTimeline)
class CaseTimelineAdmin(admin.ModelAdmin):
    """Admin interface for timeline events"""

    list_display = [
        'id',
        'event_badge',
        'case_link',
        'user',
        'created_at'
    ]

    list_filter = [
        'event_type',
        'created_at',
        'case__status'
    ]

    search_fields = [
        'description',
        'case__title',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]

    readonly_fields = [
        'case',
        'event_type',
        'description',
        'user',
        'metadata',
        'created_at',
        'event_badge'
    ]

    fieldsets = (
        ('Evento', {
            'fields': ('event_type', 'event_badge', 'description')
        }),
        ('Relacionamento', {
            'fields': ('case', 'user', 'created_at')
        }),
        ('Metadados', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )

    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Prevent manual timeline creation - only via signals"""
        return False

    def has_change_permission(self, request, obj=None):
        """Timeline events are immutable"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit trail"""
        return request.user.is_superuser

    def event_badge(self, obj):
        """Display colored event badge"""
        colors = {
            'case_created': '#28a745',
            'submitted_for_approval': '#007bff',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'bank_info_submitted': '#17a2b8',
            'transfer_confirmed': '#28a745',
            'member_proof_submitted': '#17a2b8',
            'completed': '#28a745',
            'attachment_uploaded': '#6c757d',
            'status_changed': '#ffc107',
            'comment_added': '#6c757d',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.event_type, '#000'),
            obj.get_event_type_display()
        )
    event_badge.short_description = "Tipo de Evento"

    def case_link(self, obj):
        """Link to related case"""
        if obj.case:
            url = reverse('admin:assistance_assistancecase_change', args=[obj.case.id])
            return format_html('<a href="{}">{}</a>', url, obj.case.title)
        return "-"
    case_link.short_description = "Caso"


@admin.register(AssistanceCase)
class AssistanceCaseAdmin(admin.ModelAdmin):
    """Admin interface for assistance cases"""

    list_display = [
        'id',
        'title',
        'status_badge',
        'total_value',
        'created_by',
        'created_at',
        'reviewed_by',
        'approved_at',
        'attachment_count'
    ]

    list_filter = [
        'status',
        'created_at',
        'approved_at',
        'created_by__role',
        'reviewed_by__role'
    ]

    search_fields = [
        'title',
        'public_description',
        'internal_description',
        'created_by__email',
        'created_by__first_name',
        'created_by__last_name'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'approved_at',
        'attachment_count',
        'status_badge',
        'creator_info',
        'reviewer_info'
    ]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'public_description', 'total_value')
        }),
        ('Descrição Interna', {
            'fields': ('internal_description',),
            'description': 'Informação confidencial para Conselho Diretor e Fiscal'
        }),
        ('Status & Workflow', {
            'fields': ('status', 'status_badge', 'rejection_reason')
        }),
        ('Criação', {
            'fields': ('created_by', 'creator_info', 'created_at')
        }),
        ('Revisão', {
            'fields': ('reviewed_by', 'reviewer_info', 'approved_at')
        }),
        ('Metadados', {
            'fields': ('updated_at', 'attachment_count'),
            'classes': ('collapse',)
        })
    )

    inlines = [CaseTimelineInline, AttachmentInline]

    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    actions = ['approve_cases', 'reject_cases', 'mark_as_pending']

    def status_badge(self, obj):
        """Display colored status badge"""
        colors = {
            'draft': '#6c757d',  # Gray
            'pending_approval': '#ffc107',  # Yellow
            'approved': '#28a745',  # Green
            'rejected': '#dc3545'  # Red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'),
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def creator_info(self, obj):
        """Show creator info with link"""
        if obj.created_by:
            url = reverse('admin:users_user_change', args=[obj.created_by.id])
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.created_by.get_full_name(),
                obj.created_by.get_role_display()
            )
        return "-"
    creator_info.short_description = "Criado por (detalhes)"

    def reviewer_info(self, obj):
        """Show reviewer info with link"""
        if obj.reviewed_by:
            url = reverse('admin:users_user_change', args=[obj.reviewed_by.id])
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.reviewed_by.get_full_name(),
                obj.reviewed_by.get_role_display()
            )
        return "-"
    reviewer_info.short_description = "Revisado por (detalhes)"

    def approve_cases(self, request, queryset):
        """Bulk approve pending cases"""
        pending_cases = queryset.filter(status='pending_approval')
        count = 0
        for case in pending_cases:
            if case.approve(reviewer_user=request.user):
                count += 1
        self.message_user(request, f"{count} caso(s) aprovado(s) com sucesso.")
    approve_cases.short_description = "Aprovar casos selecionados"

    def reject_cases(self, request, queryset):
        """Bulk reject pending cases (requires reason)"""
        pending_cases = queryset.filter(status='pending_approval')
        count = 0
        reason = "Rejeitado em massa via Django Admin"
        for case in pending_cases:
            if case.reject(reviewer_user=request.user, reason=reason):
                count += 1
        self.message_user(request, f"{count} caso(s) rejeitado(s) com sucesso.")
    reject_cases.short_description = "Rejeitar casos selecionados"

    def mark_as_pending(self, request, queryset):
        """Mark draft cases as pending"""
        draft_cases = queryset.filter(status='draft')
        count = 0
        for case in draft_cases:
            if case.submit_for_approval():
                count += 1
        self.message_user(request, f"{count} caso(s) enviado(s) para aprovação.")
    mark_as_pending.short_description = "Enviar rascunhos para aprovação"


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Admin interface for attachments"""

    list_display = [
        'id',
        'file_name',
        'file_type',
        'file_size_mb',
        'case_link',
        'uploaded_by',
        'uploaded_at',
        'file_preview'
    ]

    list_filter = [
        'file_type',
        'uploaded_at',
        'case__status'
    ]

    search_fields = [
        'file_name',
        'case__title',
        'uploaded_by__email'
    ]

    readonly_fields = [
        'file_name',
        'file_type',
        'file_size',
        'file_size_mb',
        'uploaded_at',
        'uploaded_by',
        'file_preview',
        'is_image',
        'is_pdf'
    ]

    fieldsets = (
        ('Arquivo', {
            'fields': ('file', 'file_preview')
        }),
        ('Metadados', {
            'fields': ('file_name', 'file_type', 'file_size_mb', 'is_image', 'is_pdf')
        }),
        ('Relacionamento', {
            'fields': ('case', 'uploaded_by', 'uploaded_at')
        })
    )

    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']

    def case_link(self, obj):
        """Link to related case"""
        if obj.case:
            url = reverse('admin:assistance_assistancecase_change', args=[obj.case.id])
            return format_html('<a href="{}">{}</a>', url, obj.case.title)
        return "-"
    case_link.short_description = "Caso"

    def file_preview(self, obj):
        """Show file preview"""
        if obj.pk and obj.file:
            if obj.is_image:
                return format_html(
                    '<a href="{}" target="_blank"><img src="{}" style="max-height: 100px; max-width: 200px;"/></a>',
                    obj.file.url,
                    obj.file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank" style="font-size: 14px;">📄 Baixar {}</a>',
                    obj.file.url,
                    obj.file_name
                )
        return "-"
    file_preview.short_description = "Preview"
