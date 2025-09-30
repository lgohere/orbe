"""
Assistance module models for managing social assistance cases.

This module handles the core workflow of the ORBE platform:
1. Board members create assistance cases with documentation
2. Fiscal Council members review and approve/reject cases
3. Approved cases are published to the public feed
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User
import os


class AssistanceCase(models.Model):
    """
    Represents a social assistance case requiring approval.

    Workflow:
    - Board creates case in 'draft' status
    - Board submits case → 'pending_approval'
    - Fiscal Council reviews → 'approved' or 'rejected'
    - Approved cases appear in public feed
    """

    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('pending_approval', 'Pendente de Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    # Basic Information
    title = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título resumido do caso (visível publicamente após aprovação)'
    )

    public_description = models.TextField(
        verbose_name='Descrição Pública',
        help_text='Descrição que será exibida no feed após aprovação'
    )

    internal_description = models.TextField(
        verbose_name='Descrição Interna',
        help_text='Informações confidenciais para Conselho Diretor e Fiscal apenas'
    )

    # Financial
    total_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor Total',
        help_text='Valor solicitado para o caso (R$)'
    )

    # Status & Workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status',
        db_index=True
    )

    # Relationships
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_cases',
        verbose_name='Criado por',
        help_text='Membro do Conselho Diretor que criou o caso'
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_cases',
        verbose_name='Revisado por',
        help_text='Membro do Conselho Fiscal que aprovou/rejeitou'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Aprovado em'
    )

    # Rejection
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='Motivo da Rejeição',
        help_text='Explicação do Conselho Fiscal sobre a rejeição'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Caso de Assistência'
        verbose_name_plural = 'Casos de Assistência'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_draft(self):
        """Check if case is in draft status"""
        return self.status == 'draft'

    @property
    def is_pending(self):
        """Check if case is pending approval"""
        return self.status == 'pending_approval'

    @property
    def is_approved(self):
        """Check if case is approved"""
        return self.status == 'approved'

    @property
    def is_rejected(self):
        """Check if case is rejected"""
        return self.status == 'rejected'

    def submit_for_approval(self):
        """
        Submit draft case for approval.
        Only draft cases can be submitted.
        """
        if self.status == 'draft':
            self.status = 'pending_approval'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def approve(self, reviewer_user):
        """
        Approve case by Fiscal Council member.
        Sets approved status and timestamp.
        """
        if self.status == 'pending_approval':
            self.status = 'approved'
            self.reviewed_by = reviewer_user
            self.approved_at = timezone.now()
            self.rejection_reason = ''  # Clear any previous rejection
            self.save(update_fields=['status', 'reviewed_by', 'approved_at', 'rejection_reason', 'updated_at'])
            return True
        return False

    def reject(self, reviewer_user, reason):
        """
        Reject case by Fiscal Council member.
        Requires rejection reason.
        """
        if self.status == 'pending_approval' and reason:
            self.status = 'rejected'
            self.reviewed_by = reviewer_user
            self.rejection_reason = reason
            self.approved_at = None  # Clear approval timestamp
            self.save(update_fields=['status', 'reviewed_by', 'rejection_reason', 'approved_at', 'updated_at'])
            return True
        return False

    @property
    def attachment_count(self):
        """Get number of attachments"""
        return self.attachments.count()

    @property
    def can_be_edited(self):
        """Check if case can be edited (only drafts and rejected)"""
        return self.status in ['draft', 'rejected']


class Attachment(models.Model):
    """
    File attachment for assistance cases.

    Supports multiple file types (PDF, images) for documentation
    such as receipts, invoices, photos, medical reports, etc.
    """

    ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    case = models.ForeignKey(
        AssistanceCase,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Caso'
    )

    file = models.FileField(
        upload_to='assistance_attachments/%Y/%m/',
        verbose_name='Arquivo',
        help_text='PDF, imagem ou documento (máx. 5MB)'
    )

    file_name = models.CharField(
        max_length=255,
        verbose_name='Nome do Arquivo',
        help_text='Nome original do arquivo'
    )

    file_type = models.CharField(
        max_length=50,
        verbose_name='Tipo de Arquivo',
        help_text='Extensão do arquivo (PDF, JPG, PNG, etc.)'
    )

    file_size = models.IntegerField(
        verbose_name='Tamanho',
        help_text='Tamanho do arquivo em bytes'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Enviado em'
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_attachments',
        verbose_name='Enviado por'
    )

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Anexo'
        verbose_name_plural = 'Anexos'

    def __str__(self):
        return f"{self.file_name} ({self.case.title})"

    def save(self, *args, **kwargs):
        """
        Override save to extract file metadata.
        Sets file_name, file_type, and file_size automatically.
        """
        if self.file and not self.file_name:
            # Extract original filename
            self.file_name = os.path.basename(self.file.name)

            # Extract file extension
            _, ext = os.path.splitext(self.file_name)
            self.file_type = ext.upper().replace('.', '')

            # Get file size
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size

        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        """Get file size in megabytes"""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def is_image(self):
        """Check if file is an image"""
        return self.file_type.lower() in ['jpg', 'jpeg', 'png', 'gif']

    @property
    def is_pdf(self):
        """Check if file is a PDF"""
        return self.file_type.lower() == 'pdf'

    @property
    def file_icon(self):
        """Get Material Design icon for file type"""
        if self.is_image:
            return 'mdi-file-image'
        elif self.is_pdf:
            return 'mdi-file-pdf-box'
        elif self.file_type.lower() in ['doc', 'docx']:
            return 'mdi-file-word'
        else:
            return 'mdi-file-document'
