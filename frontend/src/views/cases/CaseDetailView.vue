<template>
  <v-container fluid>
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p class="text-body-1 text-grey mt-4">Carregando caso...</p>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Case Detail -->
    <div v-else-if="caseData">
      <!-- Header -->
      <v-row class="mb-4">
        <v-col cols="12">
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            @click="$router.push('/cases')"
            class="mb-2"
          >
            Voltar para Lista
          </v-btn>

          <div class="d-flex align-center justify-space-between flex-wrap gap-2">
            <div>
              <h1 class="text-h4 font-weight-bold text-primary mb-2">
                {{ caseData.title }}
              </h1>
              <div class="d-flex align-center gap-2 flex-wrap">
                <v-chip :color="getStatusColor(caseData.status)" size="large">
                  <v-icon start>{{ getStatusIcon(caseData.status) }}</v-icon>
                  {{ caseData.status_display }}
                </v-chip>
                <span class="text-body-2 text-grey">
                  Criado em {{ formatDate(caseData.created_at) }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="d-flex gap-2 mt-2 flex-wrap">
              <!-- Edit (Draft/Pending only) -->
              <v-btn
                v-if="canEdit"
                color="primary"
                variant="outlined"
                prepend-icon="mdi-pencil"
                @click="$router.push(`/cases/${caseData.id}/edit`)"
              >
                Editar
              </v-btn>

              <!-- Submit for Approval (Draft only) -->
              <v-btn
                v-if="canSubmit"
                color="primary"
                prepend-icon="mdi-send"
                @click="submitForApproval"
                :loading="submitting"
              >
                Enviar para Aprovação
              </v-btn>

              <!-- Approve (Pending Approval) -->
              <v-btn
                v-if="canApprove"
                color="success"
                prepend-icon="mdi-check"
                @click="showApprovalDialog = true"
              >
                Aprovar
              </v-btn>

              <!-- Reject (Pending Approval) -->
              <v-btn
                v-if="canApprove"
                color="error"
                prepend-icon="mdi-close"
                @click="showRejectionDialog = true"
              >
                Rejeitar
              </v-btn>

              <!-- Submit Bank Info (Awaiting Bank Info - Member only) -->
              <v-btn
                v-if="canSubmitBankInfo"
                color="blue-grey"
                prepend-icon="mdi-bank"
                @click="showBankInfoDialog = true"
              >
                Informar Dados Bancários
              </v-btn>

              <!-- Confirm Transfer (Awaiting Transfer - Admin only) -->
              <v-btn
                v-if="canConfirmTransfer"
                color="info"
                prepend-icon="mdi-bank-transfer"
                @click="openTransferDialog"
              >
                Confirmar Transferência
              </v-btn>

              <!-- Submit Member Proof (Awaiting Member Proof - Member only) -->
              <v-btn
                v-if="canSubmitMemberProof"
                color="purple"
                prepend-icon="mdi-camera"
                @click="showSubmitProofDialog = true"
              >
                Enviar Comprovantes
              </v-btn>

              <!-- Complete Case (Pending Validation - Admin only) -->
              <v-btn
                v-if="canComplete"
                color="success"
                prepend-icon="mdi-check-all"
                @click="showCompleteDialog = true"
              >
                Validar e Concluir
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <!-- Main Content -->
        <v-col cols="12" md="8">
          <!-- Public Description -->
          <v-card class="mb-4">
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-text-box-outline</v-icon>
              Descrição Pública
            </v-card-title>
            <v-card-text class="text-body-1" style="white-space: pre-wrap;">
              {{ caseData.public_description }}
            </v-card-text>
          </v-card>

          <!-- Internal Description (if has permission) -->
          <v-card v-if="caseData.internal_description" class="mb-4">
            <v-card-title class="text-h6 bg-warning-lighten-4">
              <v-icon class="mr-2">mdi-lock-outline</v-icon>
              Descrição Interna (Confidencial)
            </v-card-title>
            <v-card-text class="text-body-1 internal-description-content">
              <div v-html="formattedInternalDescription"></div>
            </v-card-text>
          </v-card>

          <!-- Rejection Reason (if rejected) -->
          <v-card v-if="caseData.rejection_reason" class="mb-4" color="error-lighten-5">
            <v-card-title class="text-h6">
              <v-icon class="mr-2" color="error">mdi-alert-circle-outline</v-icon>
              Motivo da Rejeição
            </v-card-title>
            <v-card-text class="text-body-1" style="white-space: pre-wrap;">
              {{ caseData.rejection_reason }}
            </v-card-text>
          </v-card>

          <!-- Attachments -->
          <v-card>
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-paperclip</v-icon>
              Anexos ({{ caseData.attachments?.length || 0 }})
            </v-card-title>
            <v-card-text v-if="!caseData.attachments || caseData.attachments.length === 0">
              <p class="text-grey text-center py-4">Nenhum anexo adicionado</p>
            </v-card-text>
            <v-list v-else>
              <v-list-item
                v-for="attachment in caseData.attachments"
                :key="attachment.id"
                :href="attachment.file_url"
                target="_blank"
              >
                <template #prepend>
                  <v-avatar :color="getAttachmentColor(attachment.attachment_type)">
                    <v-icon :color="getAttachmentIconColor(attachment.attachment_type)">
                      {{ getAttachmentIcon(attachment.attachment_type) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ attachment.file_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip size="x-small" class="mr-2">{{ getAttachmentTypeLabel(attachment.attachment_type) }}</v-chip>
                  {{ attachment.file_type }} •  {{ attachment.file_size_mb }} MB •
                  Enviado em {{ formatDate(attachment.uploaded_at) }}
                </v-list-item-subtitle>

                <template #append>
                  <v-btn
                    icon="mdi-download"
                    variant="text"
                    size="small"
                    :href="attachment.file_url"
                    download
                  />
                  <v-btn
                    v-if="canDeleteAttachment(attachment)"
                    icon="mdi-delete"
                    variant="text"
                    size="small"
                    color="error"
                    @click.prevent="confirmDeleteAttachment(attachment)"
                  />
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>

        <!-- Sidebar -->
        <v-col cols="12" md="4">
          <!-- Summary Card -->
          <v-card class="mb-4">
            <v-card-title class="text-h6 bg-primary text-white">
              <v-icon class="mr-2">mdi-information-outline</v-icon>
              Informações
            </v-card-title>
            <v-list>
              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Valor Total</v-list-item-title>
                <v-list-item-subtitle class="text-h6 font-weight-bold text-success">
                  {{ formatCurrency(caseData.total_value) }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider />

              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Criado por</v-list-item-title>
                <v-list-item-subtitle>
                  {{ caseData.created_by?.full_name || caseData.created_by?.email }}
                  <v-chip size="x-small" class="ml-1">{{ getRoleLabel(caseData.created_by?.role) }}</v-chip>
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider />

              <v-list-item v-if="caseData.reviewed_by">
                <v-list-item-title class="text-caption text-grey">Revisado por</v-list-item-title>
                <v-list-item-subtitle>
                  {{ caseData.reviewed_by.full_name || caseData.reviewed_by.email }}
                  <v-chip size="x-small" class="ml-1">{{ getRoleLabel(caseData.reviewed_by.role) }}</v-chip>
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider v-if="caseData.reviewed_by" />

              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Última Atualização</v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatDate(caseData.updated_at) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card>

          <!-- Progress Timeline Card -->
          <v-card>
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-timeline-clock-outline</v-icon>
              Histórico do Caso
            </v-card-title>

            <!-- Empty State -->
            <v-card-text v-if="!caseData.timeline_events || caseData.timeline_events.length === 0" class="text-center py-8">
              <v-icon size="64" color="grey-lighten-2">mdi-timeline-clock-outline</v-icon>
              <p class="text-grey mt-2">Nenhum evento registrado ainda</p>
            </v-card-text>

            <!-- Dynamic Timeline -->
            <v-timeline v-else side="end" density="compact" class="pa-4">
              <v-timeline-item
                v-for="event in caseData.timeline_events"
                :key="event.id"
                :dot-color="event.event_color"
                :icon="event.event_icon"
                size="small"
              >
                <div>
                  <div class="font-weight-bold">{{ event.event_display }}</div>

                  <!-- Description (if available) -->
                  <div v-if="event.description" class="text-body-2 mt-1" style="white-space: pre-wrap;">
                    {{ event.description }}
                  </div>

                  <!-- User and Date -->
                  <div class="text-caption text-grey mt-1">
                    {{ event.user_name }} • {{ formatDate(event.created_at) }}
                  </div>

                  <!-- Metadata (for specific events) -->
                  <div v-if="event.metadata && Object.keys(event.metadata).length > 0" class="mt-2">
                    <!-- Bank Info metadata -->
                    <v-chip
                      v-if="event.event_type === 'bank_info_submitted' && event.metadata.beneficiary_name"
                      size="small"
                      variant="tonal"
                      color="info"
                      class="mr-1"
                    >
                      <v-icon start size="small">mdi-account</v-icon>
                      {{ event.metadata.beneficiary_name }}
                    </v-chip>
                    <v-chip
                      v-if="event.event_type === 'bank_info_submitted' && event.metadata.beneficiary_bank"
                      size="small"
                      variant="tonal"
                      color="info"
                      class="mr-1"
                    >
                      <v-icon start size="small">mdi-bank</v-icon>
                      {{ event.metadata.beneficiary_bank }}
                    </v-chip>

                    <!-- Attachment metadata -->
                    <v-chip
                      v-if="event.event_type === 'attachment_uploaded' && event.metadata.file_name"
                      size="small"
                      variant="tonal"
                      color="grey"
                    >
                      <v-icon start size="small">{{ event.event_icon }}</v-icon>
                      {{ event.metadata.file_name }}
                    </v-chip>
                  </div>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Bank Info Dialog -->
    <BankInfoDialog
      v-if="caseData"
      v-model="showBankInfoDialog"
      :case-id="caseData.id"
      @submitted="onBankInfoSubmitted"
    />

    <!-- Transfer Proof Dialog (Admin) -->
    <TransferProofDialog
      v-model="showConfirmTransferDialog"
      :case-data="caseData"
      @success="onTransferConfirmed"
    />

    <!-- Member Proof Dialog -->
    <MemberProofDialog
      v-model="showSubmitProofDialog"
      :case-data="caseData"
      @success="onMemberProofSubmitted"
    />

    <!-- Complete Case Dialog (Admin) -->
    <CompleteCaseDialog
      v-model="showCompleteDialog"
      :case-data="caseData"
      @success="onCaseCompleted"
    />

    <!-- Delete Attachment Confirmation Dialog -->
    <v-dialog v-model="showDeleteAttachmentDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6 bg-error text-white">
          <v-icon class="mr-2" color="white">mdi-alert-circle</v-icon>
          Confirmar Exclusão
        </v-card-title>

        <v-card-text class="pt-6">
          <p class="text-body-1">
            Tem certeza que deseja remover este anexo?
          </p>
          <v-alert v-if="attachmentToDelete" type="info" variant="tonal" class="mt-4">
            <strong>Arquivo:</strong> {{ attachmentToDelete.file_name }}<br>
            <strong>Tipo:</strong> {{ getAttachmentTypeLabel(attachmentToDelete.attachment_type) }}<br>
            <strong>Tamanho:</strong> {{ attachmentToDelete.file_size_mb }} MB
          </v-alert>
          <v-alert type="warning" variant="tonal" class="mt-4">
            <strong>Atenção:</strong> Esta ação não pode ser desfeita!
          </v-alert>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            @click="showDeleteAttachmentDialog = false"
            :disabled="deletingAttachment"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="deletingAttachment"
            @click="deleteAttachment"
          >
            Remover Anexo
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Success Snackbar -->
    <v-snackbar v-model="showSuccess" color="success" timeout="3000">
      {{ successMessage }}
    </v-snackbar>

    <!-- Error Snackbar -->
    <v-snackbar v-model="showError" color="error" timeout="5000">
      {{ error }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import BankInfoDialog from '@/components/assistance/BankInfoDialog.vue'
import TransferProofDialog from '@/components/assistance/TransferProofDialog.vue'
import MemberProofDialog from '@/components/assistance/MemberProofDialog.vue'
import CompleteCaseDialog from '@/components/assistance/CompleteCaseDialog.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const caseData = ref<any>(null)
const loading = ref(false)
const error = ref('')
const submitting = ref(false)
const approving = ref(false)
const rejecting = ref(false)
const showApprovalDialog = ref(false)
const showRejectionDialog = ref(false)
const showBankInfoDialog = ref(false)
const showConfirmTransferDialog = ref(false)
const showSubmitProofDialog = ref(false)
const showCompleteDialog = ref(false)
const rejectionReason = ref('')
const showSuccess = ref(false)
const successMessage = ref('')
const showError = ref(false)
const showDeleteAttachmentDialog = ref(false)
const attachmentToDelete = ref<any>(null)
const deletingAttachment = ref(false)

// Computed
const canEdit = computed(() =>
  caseData.value?.can_be_edited &&
  (caseData.value?.created_by?.id === authStore.user?.id || authStore.isAdmin)
)

const canSubmit = computed(() =>
  caseData.value?.status === 'draft' &&
  (caseData.value?.created_by?.id === authStore.user?.id || authStore.isAdmin)
)

const canApprove = computed(() =>
  caseData.value?.status === 'pending_approval' &&
  authStore.canApproveCases
)

const canSubmitBankInfo = computed(() =>
  caseData.value?.status === 'awaiting_bank_info' &&
  caseData.value?.created_by?.id === authStore.user?.id
)

const canConfirmTransfer = computed(() =>
  caseData.value?.status === 'awaiting_transfer' &&
  authStore.canApproveCases
)

const canSubmitMemberProof = computed(() =>
  caseData.value?.status === 'awaiting_member_proof' &&
  caseData.value?.created_by?.id === authStore.user?.id
)

const canComplete = computed(() =>
  caseData.value?.status === 'pending_validation' &&
  authStore.canApproveCases
)

// Methods
async function loadCase() {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`/api/assistance/cases/${route.params.id}/`, {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) {
      if (response.status === 404) {
        error.value = 'Caso não encontrado'
      } else {
        error.value = 'Erro ao carregar caso'
      }
      return
    }

    caseData.value = await response.json()
  } catch (err) {
    console.error('Error loading case:', err)
    error.value = 'Erro ao carregar caso'
  } finally {
    loading.value = false
  }
}

async function submitForApproval() {
  submitting.value = true

  try {
    const response = await fetch(`/api/assistance/cases/${caseData.value.id}/submit/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = data.error || 'Erro ao enviar caso para aprovação'
      return
    }

    successMessage.value = 'Caso enviado para aprovação com sucesso!'
    showSuccess.value = true
    await loadCase()
  } catch (err) {
    console.error('Error submitting case:', err)
    error.value = 'Erro ao enviar caso'
  } finally {
    submitting.value = false
  }
}

async function approveCase() {
  approving.value = true

  try {
    const response = await fetch(`/api/assistance/cases/${caseData.value.id}/approve/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = data.error || 'Erro ao aprovar caso'
      return
    }

    showApprovalDialog.value = false
    successMessage.value = 'Caso aprovado! Um AssistanceCase foi criado automaticamente.'
    showSuccess.value = true
    await loadCase()
  } catch (err) {
    console.error('Error approving case:', err)
    error.value = 'Erro ao aprovar caso'
  } finally {
    approving.value = false
  }
}

async function rejectCase() {
  rejecting.value = true

  try {
    const response = await fetch(`/api/assistance/cases/${caseData.value.id}/reject/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        rejection_reason: rejectionReason.value
      })
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = data.rejection_reason?.[0] || data.error || 'Erro ao rejeitar caso'
      return
    }

    showRejectionDialog.value = false
    successMessage.value = 'Caso rejeitado'
    showSuccess.value = true
    await loadCase()
    rejectionReason.value = ''
  } catch (err) {
    console.error('Error rejecting case:', err)
    error.value = 'Erro ao rejeitar caso'
  } finally {
    rejecting.value = false
  }
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    'draft': 'grey',
    'pending_approval': 'warning',
    'awaiting_bank_info': 'blue-grey',
    'awaiting_transfer': 'info',
    'awaiting_member_proof': 'purple',
    'pending_validation': 'deep-orange',
    'completed': 'success',
    'rejected': 'error'
  }
  return colors[status] || 'grey'
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    'draft': 'mdi-pencil-outline',
    'pending_approval': 'mdi-clock-outline',
    'awaiting_bank_info': 'mdi-bank',
    'awaiting_transfer': 'mdi-bank-transfer',
    'awaiting_member_proof': 'mdi-camera-outline',
    'pending_validation': 'mdi-shield-check-outline',
    'completed': 'mdi-check-circle',
    'rejected': 'mdi-close-circle-outline'
  }
  return icons[status] || 'mdi-file-document-outline'
}

function getAttachmentColor(type: string): string {
  const colors: Record<string, string> = {
    'payment_proof': 'info-lighten-4',
    'photo_evidence': 'purple-lighten-4',
    'other': 'grey-lighten-3'
  }
  return colors[type] || 'grey-lighten-3'
}

function getAttachmentIconColor(type: string): string {
  const colors: Record<string, string> = {
    'payment_proof': 'info',
    'photo_evidence': 'purple',
    'other': 'grey'
  }
  return colors[type] || 'grey'
}

function getAttachmentIcon(type: string): string {
  const icons: Record<string, string> = {
    'payment_proof': 'mdi-receipt',
    'photo_evidence': 'mdi-camera',
    'other': 'mdi-file-document'
  }
  return icons[type] || 'mdi-paperclip'
}

function getAttachmentTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    'payment_proof': 'Comprovante de Pagamento',
    'photo_evidence': 'Foto/Comprovante',
    'other': 'Outro'
  }
  return labels[type] || type
}

function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    'SUPER_ADMIN': 'Admin',
    'BOARD': 'Conselho Diretor',
    'FISCAL_COUNCIL': 'Conselho Fiscal',
    'MEMBER': 'Membro'
  }
  return labels[role] || role
}

function formatCurrency(value: string): string {
  const num = parseFloat(value)
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(num)
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'long',
    timeStyle: 'short'
  }).format(date)
}

// Computed property para converter markdown simples em HTML
const formattedInternalDescription = computed(() => {
  if (!caseData.value?.internal_description) return ''

  let html = caseData.value.internal_description

  // Escape HTML para prevenir XSS
  html = html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Converter markdown patterns para HTML
  // **bold** → <strong>bold</strong>
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // *italic* → <em>italic</em>
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')

  // Line breaks → <br>
  html = html.replace(/\n/g, '<br>')

  return html
})

async function onBankInfoSubmitted() {
  showBankInfoDialog.value = false  // Garantir fechamento do dialog
  successMessage.value = 'Dados bancários enviados com sucesso! Aguardando transferência do admin.'
  showSuccess.value = true
  await loadCase()
}

function openTransferDialog() {
  console.log('Opening transfer dialog, current status:', caseData.value?.status)
  console.log('Can approve cases:', authStore.canApproveCases)
  console.log('Current showConfirmTransferDialog:', showConfirmTransferDialog.value)
  showConfirmTransferDialog.value = true
  console.log('After setting showConfirmTransferDialog:', showConfirmTransferDialog.value)
}

async function onTransferConfirmed() {
  showConfirmTransferDialog.value = false  // Garantir fechamento do dialog
  successMessage.value = 'Transferência confirmada! Aguardando comprovação do membro.'
  showSuccess.value = true
  await loadCase()
}

async function onMemberProofSubmitted() {
  showSubmitProofDialog.value = false  // Garantir fechamento do dialog
  successMessage.value = 'Comprovantes enviados! Aguardando validação do administrador.'
  showSuccess.value = true
  await loadCase()
}

async function onCaseCompleted() {
  showCompleteCaseDialog.value = false  // Garantir fechamento do dialog
  successMessage.value = 'Caso validado e concluído com sucesso! 🎉'
  showSuccess.value = true
  await loadCase()
}

// Attachment deletion
function canDeleteAttachment(attachment: any): boolean {
  // Admin can always delete
  if (authStore.isAdmin) return true

  // Can't delete from completed cases
  if (caseData.value?.status === 'completed') return false

  // CRITICAL: Users can ONLY delete their own uploads
  // Members CANNOT delete admin's attachments (payment_proof)
  if (attachment.uploaded_by?.id === authStore.user?.id) return true

  return false
}

function confirmDeleteAttachment(attachment: any) {
  attachmentToDelete.value = attachment
  showDeleteAttachmentDialog.value = true
}

async function deleteAttachment() {
  if (!attachmentToDelete.value) return

  deletingAttachment.value = true

  try {
    console.log('Deleting attachment:', attachmentToDelete.value.id)
    const result = await api.deleteAttachment(attachmentToDelete.value.id)
    console.log('Delete result:', result)

    if (result.error) {
      console.error('Delete error:', result.error)
      error.value = result.error
      showError.value = true
      showDeleteAttachmentDialog.value = false
    } else {
      successMessage.value = 'Anexo removido com sucesso!'
      showSuccess.value = true
      showDeleteAttachmentDialog.value = false
      attachmentToDelete.value = null
      await loadCase()
    }
  } catch (err: any) {
    console.error('Exception during delete:', err)
    error.value = err.message || 'Erro ao remover anexo'
    showError.value = true
    showDeleteAttachmentDialog.value = false
  } finally {
    deletingAttachment.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadCase()
})
</script>

<style scoped>
.gap-2 {
  gap: 0.5rem;
}

/* Professional formatting for internal description markdown */
.internal-description-content {
  line-height: 1.8;
  color: #2c3e50;
}

.internal-description-content :deep(strong) {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 1.05em;
}

.internal-description-content :deep(em) {
  font-style: italic;
  color: #555;
}

.internal-description-content :deep(br) {
  margin-bottom: 0.5rem;
}
</style>
