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
    Represents a social assistance case tracking donation execution.

    Workflow:
    1. Created automatically when DonationRequest is approved → 'awaiting_proof'
    2. Member executes donation and uploads proof → 'proof_submitted'
    3. Admin validates proof → 'completed'
    4. Published in feed for transparency

    OR (manual creation by Board):
    - Board creates case in 'draft' status
    - Board submits case → 'pending_approval'
    - Admin reviews → 'approved' or 'rejected'
    """

    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('pending_approval', 'Pendente de Aprovação'),
        ('awaiting_bank_info', 'Aguardando Dados Bancários'),
        ('awaiting_transfer', 'Aguardando Transferência do Admin'),
        ('awaiting_member_proof', 'Aguardando Comprovação do Membro'),
        ('pending_validation', 'Pendente de Validação Final'),
        ('completed', 'Concluído'),
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
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status',
        db_index=True
    )

    # Relationships
    donation_request = models.OneToOneField(
        'finance.DonationRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assistance_case',
        verbose_name='Solicitação de Doação',
        help_text='Solicitação que originou este caso (se aplicável)'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_cases',
        verbose_name='Criado por',
        help_text='Membro que criou/solicitou o caso'
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_cases',
        verbose_name='Revisado por',
        help_text='Admin que validou o caso/comprovantes'
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

    transfer_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Transferência Confirmada em',
        help_text='Data em que admin confirmou a transferência ao membro'
    )

    member_proof_submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Comprovante do Membro Enviado em',
        help_text='Data em que o membro enviou comprovantes da aplicação ao beneficiário'
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Concluído em',
        help_text='Data em que o admin validou e finalizou o caso'
    )

    bank_info_submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Dados Bancários Informados em',
        help_text='Data em que o membro informou os dados bancários do beneficiário'
    )

    # Bank Information (beneficiary)
    beneficiary_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nome do Beneficiário',
        help_text='Nome completo do beneficiário da doação'
    )

    beneficiary_cpf = models.CharField(
        max_length=14,
        blank=True,
        verbose_name='CPF do Beneficiário',
        help_text='CPF do beneficiário (formato: 000.000.000-00)'
    )

    beneficiary_bank = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Banco',
        help_text='Nome do banco (ex: Banco do Brasil, Caixa, Nubank)'
    )

    beneficiary_account_type = models.CharField(
        max_length=20,
        choices=[
            ('corrente', 'Conta Corrente'),
            ('poupanca', 'Conta Poupança'),
            ('pagamento', 'Conta Pagamento')
        ],
        blank=True,
        verbose_name='Tipo de Conta'
    )

    beneficiary_agency = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Agência',
        help_text='Número da agência (sem dígito)'
    )

    beneficiary_account = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Conta',
        help_text='Número da conta com dígito (ex: 12345-6)'
    )

    beneficiary_pix_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Chave PIX',
        help_text='Chave PIX (CPF, e-mail, telefone ou chave aleatória)'
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
        """Check if case is completed (legacy compatibility)"""
        return self.status == 'completed'

    @property
    def is_rejected(self):
        """Check if case is rejected"""
        return self.status == 'rejected'

    @property
    def is_awaiting_bank_info(self):
        """Check if case is awaiting member to provide beneficiary bank info"""
        return self.status == 'awaiting_bank_info'

    @property
    def is_awaiting_transfer(self):
        """Check if case is awaiting admin transfer confirmation"""
        return self.status == 'awaiting_transfer'

    @property
    def is_awaiting_member_proof(self):
        """Check if case is awaiting member proof submission"""
        return self.status == 'awaiting_member_proof'

    @property
    def is_pending_validation(self):
        """Check if proof was submitted and awaiting final validation"""
        return self.status == 'pending_validation'

    @property
    def is_completed(self):
        """Check if case is completed"""
        return self.status == 'completed'

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
        Approve manual case by Admin.
        Sets approved status and timestamp.
        After approval, member must provide bank info.
        """
        if self.status == 'pending_approval':
            self.status = 'awaiting_bank_info'
            self.reviewed_by = reviewer_user
            self.approved_at = timezone.now()
            self.rejection_reason = ''
            self.save(update_fields=['status', 'reviewed_by', 'approved_at', 'rejection_reason', 'updated_at'])
            return True
        return False

    def submit_bank_info(self, bank_data):
        """
        STEP 1.5: Member provides beneficiary bank information.
        Required after approval, before admin can transfer funds.
        Changes status: awaiting_bank_info → awaiting_transfer
        """
        if self.status == 'awaiting_bank_info':
            self.beneficiary_name = bank_data.get('beneficiary_name', '')
            self.beneficiary_cpf = bank_data.get('beneficiary_cpf', '')
            self.beneficiary_bank = bank_data.get('beneficiary_bank', '')
            self.beneficiary_account_type = bank_data.get('beneficiary_account_type', '')
            self.beneficiary_agency = bank_data.get('beneficiary_agency', '')
            self.beneficiary_account = bank_data.get('beneficiary_account', '')
            self.beneficiary_pix_key = bank_data.get('beneficiary_pix_key', '')
            self.bank_info_submitted_at = timezone.now()
            self.status = 'awaiting_transfer'
            self.save(update_fields=[
                'beneficiary_name', 'beneficiary_cpf', 'beneficiary_bank',
                'beneficiary_account_type', 'beneficiary_agency', 'beneficiary_account',
                'beneficiary_pix_key', 'bank_info_submitted_at', 'status', 'updated_at'
            ])
            return True
        return False

    def reject(self, reviewer_user, reason):
        """
        Reject case by Admin.
        Requires rejection reason.
        """
        if self.status in ['pending_approval', 'pending_validation'] and reason:
            self.status = 'rejected'
            self.reviewed_by = reviewer_user
            self.rejection_reason = reason
            self.approved_at = None
            self.save(update_fields=['status', 'reviewed_by', 'rejection_reason', 'approved_at', 'updated_at'])
            return True
        return False

    def confirm_transfer(self, admin_user):
        """
        STEP 2: Admin confirms they transferred/sent PIX to member.
        Must upload payment proof (bank transfer or PIX receipt).
        Changes status: awaiting_transfer → awaiting_member_proof
        """
        if self.status == 'awaiting_transfer':
            self.status = 'awaiting_member_proof'
            self.transfer_confirmed_at = timezone.now()
            self.save(update_fields=['status', 'transfer_confirmed_at', 'updated_at'])
            return True
        return False

    def submit_member_proof(self):
        """
        STEP 3: Member submits proof of application to beneficiary.
        Member uploads photos + receipts showing donation was properly applied.
        Changes status: awaiting_member_proof → pending_validation
        """
        if self.status == 'awaiting_member_proof':
            self.status = 'pending_validation'
            self.member_proof_submitted_at = timezone.now()
            self.save(update_fields=['status', 'member_proof_submitted_at', 'updated_at'])
            return True
        return False

    def complete(self, reviewer_user):
        """
        STEP 4: Admin validates all proofs and completes case.
        Admin reviews transfer proof + member application proof.
        If satisfied, marks case as completed and publishes to feed.
        Changes status: pending_validation → completed
        """
        if self.status == 'pending_validation':
            self.status = 'completed'
            self.reviewed_by = reviewer_user
            self.completed_at = timezone.now()
            self.save(update_fields=['status', 'reviewed_by', 'completed_at', 'updated_at'])
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

    def revalidate_status(self):
        """
        Revalidate case status after attachment deletion.
        Rollback to previous state if required attachments are missing.

        Called automatically by Attachment.post_delete signal.
        """
        # Completed cases are immutable - no rollback allowed
        if self.status == 'completed':
            return False

        # Check critical attachments
        has_payment_proof = self.attachments.filter(attachment_type='payment_proof').exists()
        has_photo_evidence = self.attachments.filter(attachment_type='photo_evidence').exists()

        changed = False

        # RULE 1: pending_validation requires payment_proof + photo_evidence
        if self.status == 'pending_validation':
            if not has_payment_proof and not has_photo_evidence:
                # Both missing -> rollback to awaiting_transfer
                self.status = 'awaiting_transfer'
                self.transfer_confirmed_at = None
                self.member_proof_submitted_at = None
                changed = True
            elif not has_payment_proof:
                # Only payment proof missing -> rollback to awaiting_transfer
                self.status = 'awaiting_transfer'
                self.transfer_confirmed_at = None
                self.member_proof_submitted_at = None
                changed = True
            elif not has_photo_evidence:
                # Only photo evidence missing -> rollback to awaiting_member_proof
                self.status = 'awaiting_member_proof'
                self.member_proof_submitted_at = None
                changed = True

        # RULE 2: awaiting_member_proof requires payment_proof
        elif self.status == 'awaiting_member_proof':
            if not has_payment_proof:
                self.status = 'awaiting_transfer'
                self.transfer_confirmed_at = None
                changed = True

        if changed:
            self.save(update_fields=['status', 'transfer_confirmed_at', 'member_proof_submitted_at', 'updated_at'])
            return True

        return False


class Attachment(models.Model):
    """
    File attachment for assistance cases.

    Two types:
    1. PAYMENT_PROOF: PIX/bank transfer receipts (mandatory for completion)
    2. PHOTO_EVIDENCE: Photos of delivered items/beneficiaries (optional, for transparency)
    """

    ATTACHMENT_TYPE_CHOICES = [
        ('payment_proof', 'Comprovante de Pagamento'),
        ('photo_evidence', 'Foto da Doação'),
        ('other', 'Outro Documento'),
    ]

    ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    case = models.ForeignKey(
        AssistanceCase,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Caso'
    )

    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPE_CHOICES,
        default='other',
        verbose_name='Tipo de Anexo',
        help_text='Tipo de comprovante/documento'
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


class CaseTimeline(models.Model):
    """
    Timeline tracking all events and state changes for an AssistanceCase.

    This provides complete audit trail and history visualization for:
    - Members: Track their case progress
    - Admins: Monitor all actions and changes
    - Transparency: Full accountability of the donation flow
    """

    EVENT_TYPE_CHOICES = [
        ('case_created', 'Caso Criado'),
        ('submitted_for_approval', 'Enviado para Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('bank_info_submitted', 'Dados Bancários Informados'),
        ('transfer_confirmed', 'Transferência Confirmada pelo Admin'),
        ('member_proof_submitted', 'Comprovante do Membro Enviado'),
        ('completed', 'Caso Concluído'),
        ('attachment_uploaded', 'Anexo Adicionado'),
        ('status_changed', 'Status Alterado'),
        ('comment_added', 'Comentário Adicionado'),
    ]

    case = models.ForeignKey(
        AssistanceCase,
        on_delete=models.CASCADE,
        related_name='timeline_events',
        verbose_name='Caso'
    )

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        verbose_name='Tipo de Evento',
        db_index=True
    )

    description = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada do evento'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='case_events',
        verbose_name='Usuário',
        help_text='Usuário que realizou a ação'
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadados',
        help_text='Dados adicionais do evento (JSON)'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
        db_index=True
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Evento da Timeline'
        verbose_name_plural = 'Eventos da Timeline'
        indexes = [
            models.Index(fields=['case', 'created_at']),
            models.Index(fields=['event_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.case.title} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    @classmethod
    def log_event(cls, case, event_type, user=None, description='', metadata=None):
        """
        Convenience method to log a timeline event.

        Args:
            case: AssistanceCase instance
            event_type: One of EVENT_TYPE_CHOICES
            user: User who performed the action (optional)
            description: Human-readable description (optional)
            metadata: Additional data as dict (optional)

        Returns:
            CaseTimeline instance
        """
        return cls.objects.create(
            case=case,
            event_type=event_type,
            user=user,
            description=description,
            metadata=metadata or {}
        )
