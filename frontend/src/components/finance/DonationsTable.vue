<template>
  <v-card>
    <v-card-title>
      <v-row align="center">
        <v-col cols="12" md="6">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-hand-heart</v-icon>
            <span class="text-h6">{{ title }}</span>
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="d-flex align-center justify-md-end ga-3">
            <v-text-field
              v-model="search"
              density="compact"
              label="Buscar"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              hide-details
              single-line
              style="max-width: 240px;"
            />
            <v-btn
              v-if="!isStaff"
              color="primary"
              prepend-icon="mdi-plus"
              @click="openCreateDialog"
            >
              Nova Solicitação
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-card-title>

    <v-card-text>
      <!-- Tabs for Staff -->
      <v-tabs v-if="isStaff" v-model="currentTab" color="primary" class="mb-4">
        <v-tab value="pending_approval">
          <v-icon start>mdi-clock-alert</v-icon>
          Pendentes de Aprovação
        </v-tab>
        <v-tab value="pending_proof">
          <v-icon start>mdi-file-document</v-icon>
          Pendentes de Comprovante
        </v-tab>
        <v-tab value="completed">
          <v-icon start>mdi-check-circle</v-icon>
          Concluídas
        </v-tab>
      </v-tabs>

      <v-data-table
        :headers="headers"
        :items="filteredDonations"
        :search="search"
        :items-per-page="10"
        class="elevation-0"
      >
        <!-- Requester Column (Staff only) -->
        <template v-if="isStaff" #item.requester="{ item }">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="32" class="mr-2">
              <span class="text-caption text-white">
                {{ getUserInitials(item.user_name) }}
              </span>
            </v-avatar>
            <div>
              <div class="text-body-2 font-weight-medium">{{ item.user_name }}</div>
              <div class="text-caption text-grey">{{ item.user_email }}</div>
            </div>
          </div>
        </template>

        <!-- Recipient Column -->
        <template #item.recipient="{ item }">
          <span class="font-weight-medium">{{ item.recipient }}</span>
        </template>

        <!-- Amount Column -->
        <template #item.amount="{ item }">
          <span class="font-weight-bold text-info">
            {{ formatCurrency(item.amount) }}
          </span>
        </template>

        <!-- Reason Column -->
        <template #item.reason="{ item }">
          <div class="text-truncate" style="max-width: 250px;">
            {{ item.reason }}
          </div>
        </template>

        <!-- Status Column -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            variant="flat"
            size="small"
          >
            {{ item.status_display }}
          </v-chip>
        </template>

        <!-- Created At Column -->
        <template #item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <!-- Actions Column -->
        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <!-- Member Actions -->
            <template v-if="!isStaff">
              <v-btn
                v-if="item.can_edit"
                icon="mdi-pencil"
                size="small"
                color="primary"
                variant="text"
                @click="openEditDialog(item)"
              >
                <v-icon>mdi-pencil</v-icon>
                <v-tooltip activator="parent" location="top">Editar</v-tooltip>
              </v-btn>
              <v-btn
                v-if="item.can_delete"
                icon="mdi-delete"
                size="small"
                color="error"
                variant="text"
                @click="confirmDelete(item)"
              >
                <v-icon>mdi-delete</v-icon>
                <v-tooltip activator="parent" location="top">Deletar</v-tooltip>
              </v-btn>
            </template>

            <!-- Staff Actions -->
            <template v-if="isStaff">
              <!-- PENDING_APPROVAL: Aprovar ou Rejeitar -->
              <v-btn
                v-if="item.status === 'pending_approval'"
                icon="mdi-check"
                size="small"
                color="success"
                variant="text"
                @click="approveDonation(item)"
              >
                <v-icon>mdi-check</v-icon>
                <v-tooltip activator="parent" location="top">Aprovar</v-tooltip>
              </v-btn>
              <v-btn
                v-if="item.status === 'pending_approval'"
                icon="mdi-close"
                size="small"
                color="error"
                variant="text"
                @click="openRejectDialog(item)"
              >
                <v-icon>mdi-close</v-icon>
                <v-tooltip activator="parent" location="top">Rejeitar</v-tooltip>
              </v-btn>

              <!-- APPROVED: Anexar Comprovante, Concluir ou Desaprovar -->
              <v-btn
                v-if="item.status === 'approved'"
                icon="mdi-paperclip"
                size="small"
                color="info"
                variant="text"
                @click="openAttachProofDialog(item)"
              >
                <v-icon>mdi-paperclip</v-icon>
                <v-tooltip activator="parent" location="top">Anexar Comprovante</v-tooltip>
              </v-btn>
              <v-btn
                v-if="item.status === 'approved'"
                icon="mdi-check-circle"
                size="small"
                color="success"
                variant="text"
                @click="completeDonation(item)"
              >
                <v-icon>mdi-check-circle</v-icon>
                <v-tooltip activator="parent" location="top">Marcar como Concluída</v-tooltip>
              </v-btn>
              <v-btn
                v-if="item.status === 'approved'"
                icon="mdi-arrow-u-left-top"
                size="small"
                color="warning"
                variant="text"
                @click="unapproveDonation(item)"
              >
                <v-icon>mdi-arrow-u-left-top</v-icon>
                <v-tooltip activator="parent" location="top">Desaprovar (voltar para Pendente)</v-tooltip>
              </v-btn>

              <!-- PROOF_ATTACHED: Concluir ou Remover Comprovante -->
              <v-btn
                v-if="item.status === 'proof_attached'"
                icon="mdi-check-circle"
                size="small"
                color="success"
                variant="text"
                @click="completeDonation(item)"
              >
                <v-icon>mdi-check-circle</v-icon>
                <v-tooltip activator="parent" location="top">Marcar como Concluída</v-tooltip>
              </v-btn>
              <v-btn
                v-if="item.status === 'proof_attached'"
                icon="mdi-file-remove"
                size="small"
                color="warning"
                variant="text"
                @click="removeProof(item)"
              >
                <v-icon>mdi-file-remove</v-icon>
                <v-tooltip activator="parent" location="top">Remover Comprovante</v-tooltip>
              </v-btn>

              <!-- COMPLETED or REJECTED: Reabrir -->
              <v-btn
                v-if="item.status === 'completed' || item.status === 'rejected'"
                icon="mdi-refresh"
                size="small"
                color="info"
                variant="text"
                @click="reopenDonation(item)"
              >
                <v-icon>mdi-refresh</v-icon>
                <v-tooltip activator="parent" location="top">Reabrir</v-tooltip>
              </v-btn>
            </template>

            <!-- View Details (All) -->
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="viewDetails(item)"
            >
              <v-icon>mdi-eye</v-icon>
              <v-tooltip activator="parent" location="top">Ver Detalhes</v-tooltip>
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card-text>

    <!-- Create/Edit Donation Dialog -->
    <v-dialog v-model="showFormDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="bg-primary text-white">
          <v-icon class="mr-2">mdi-hand-heart</v-icon>
          {{ isEditing ? 'Editar Solicitação' : 'Nova Solicitação de Doação' }}
        </v-card-title>

        <v-card-text class="pt-4">
          <v-form ref="formRef" v-model="formValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.recipient"
                  label="Destinatário *"
                  variant="outlined"
                  density="comfortable"
                  :rules="[v => !!v || 'Destinatário é obrigatório']"
                  placeholder="Nome da pessoa que receberá a doação"
                  required
                />
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="formattedAmount"
                  label="Valor Solicitado *"
                  variant="outlined"
                  density="comfortable"
                  prefix="R$"
                  placeholder="0,00"
                  :rules="[v => !!v || 'Valor é obrigatório']"
                  required
                  @input="handleAmountInput"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="formData.reason"
                  label="Motivo/Razão *"
                  variant="outlined"
                  density="comfortable"
                  rows="4"
                  :rules="[v => !!v || 'Motivo é obrigatório']"
                  placeholder="Ex: Compra de supermercado, Ajuda com aluguel, Medicamentos..."
                  required
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="closeFormDialog">
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-check"
            :loading="saving"
            :disabled="!formValid"
            @click="saveDonation"
          >
            {{ isEditing ? 'Atualizar' : 'Solicitar Doação' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reject Dialog -->
    <v-dialog v-model="showRejectDialog" max-width="500">
      <v-card>
        <v-card-title class="bg-error text-white">
          <v-icon class="mr-2">mdi-close-circle</v-icon>
          Rejeitar Solicitação
        </v-card-title>

        <v-card-text class="pt-4">
          <v-textarea
            v-model="rejectionReason"
            label="Motivo da Rejeição *"
            variant="outlined"
            rows="3"
            placeholder="Explique por que esta solicitação foi rejeitada..."
            :rules="[v => !!v || 'Motivo é obrigatório']"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="showRejectDialog = false">
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="rejecting"
            :disabled="!rejectionReason"
            @click="rejectDonation"
          >
            Rejeitar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Attach Proof Dialog -->
    <v-dialog v-model="showAttachProofDialog" max-width="500">
      <v-card>
        <v-card-title class="bg-info text-white">
          <v-icon class="mr-2">mdi-paperclip</v-icon>
          Anexar Comprovante
        </v-card-title>

        <v-card-text class="pt-4">
          <v-file-input
            v-model="proofFile"
            label="Comprovante (PDF) *"
            variant="outlined"
            accept=".pdf"
            prepend-icon="mdi-file-pdf-box"
            :rules="[v => !!v || 'Arquivo é obrigatório']"
            show-size
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="showAttachProofDialog = false">
            Cancelar
          </v-btn>
          <v-btn
            color="info"
            variant="flat"
            :loading="attachingProof"
            :disabled="!proofFile"
            @click="attachProof"
          >
            Anexar Comprovante
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="bg-error text-white">
          <v-icon class="mr-2">mdi-delete</v-icon>
          Confirmar Exclusão
        </v-card-title>

        <v-card-text class="pt-4">
          Tem certeza que deseja excluir esta solicitação de doação?
          Esta ação não pode ser desfeita.
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="showDeleteDialog = false">
            Cancelar
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="deleting"
            @click="deleteDonation"
          >
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="600">
      <v-card v-if="selectedDonation">
        <v-card-title class="bg-info text-white">
          <v-icon class="mr-2">mdi-hand-heart</v-icon>
          Detalhes da Solicitação
        </v-card-title>

        <v-card-text class="pt-4">
          <v-list density="comfortable">
            <v-list-item v-if="isStaff">
              <v-list-item-title class="text-caption text-grey">Solicitante</v-list-item-title>
              <v-list-item-subtitle class="text-body-1 font-weight-medium">
                {{ selectedDonation.user_name }}
                <div class="text-caption text-grey">{{ selectedDonation.user_email }}</div>
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Destinatário</v-list-item-title>
              <v-list-item-subtitle class="text-body-1 font-weight-medium">
                {{ selectedDonation.recipient }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Valor</v-list-item-title>
              <v-list-item-subtitle class="text-h6 text-info font-weight-bold">
                {{ formatCurrency(selectedDonation.amount) }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Motivo</v-list-item-title>
              <v-list-item-subtitle class="text-body-2">
                {{ selectedDonation.reason }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Status</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip
                  :color="getStatusColor(selectedDonation.status)"
                  variant="flat"
                  size="small"
                >
                  {{ selectedDonation.status_display }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Data da Solicitação</v-list-item-title>
              <v-list-item-subtitle class="text-body-1">
                {{ formatDateTime(selectedDonation.created_at) }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedDonation.reviewed_by_name">
              <v-list-item-title class="text-caption text-grey">Revisado por</v-list-item-title>
              <v-list-item-subtitle class="text-body-2">
                {{ selectedDonation.reviewed_by_name }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedDonation.rejection_reason">
              <v-list-item-title class="text-caption text-grey">Motivo da Rejeição</v-list-item-title>
              <v-list-item-subtitle class="text-body-2 text-error">
                {{ selectedDonation.rejection_reason }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedDonation.proof_document">
              <v-list-item-title class="text-caption text-grey">Comprovante</v-list-item-title>
              <v-list-item-subtitle>
                <v-btn
                  :href="selectedDonation.proof_document"
                  target="_blank"
                  size="small"
                  color="primary"
                  prepend-icon="mdi-file-pdf-box"
                >
                  Ver Comprovante
                </v-btn>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="showDetailsDialog = false">
            Fechar
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
      {{ errorMessage }}
    </v-snackbar>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Props
const props = defineProps<{
  donations: any[]
  isStaff: boolean
}>()

// Emits
const emit = defineEmits<{
  refresh: []
}>()

// State
const search = ref('')
const currentTab = ref('pending_approval')
const showFormDialog = ref(false)
const showRejectDialog = ref(false)
const showAttachProofDialog = ref(false)
const showDeleteDialog = ref(false)
const showDetailsDialog = ref(false)
const showSuccess = ref(false)
const showError = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const isEditing = ref(false)
const selectedDonation = ref<any>(null)
const formValid = ref(false)
const formRef = ref<any>(null)
const saving = ref(false)
const rejecting = ref(false)
const attachingProof = ref(false)
const deleting = ref(false)

const formData = ref({
  recipient: '',
  amount: 0,
  reason: ''
})

const formattedAmount = ref('')
const rejectionReason = ref('')
const proofFile = ref<File | null>(null)

// Computed
const title = computed(() => {
  if (props.isStaff) return 'Gerenciar Solicitações de Doação'
  return 'Minhas Solicitações'
})

const headers = computed(() => {
  const base = [
    { title: 'Destinatário', key: 'recipient', sortable: true },
    { title: 'Valor', key: 'amount', sortable: true },
    { title: 'Motivo', key: 'reason', sortable: false },
    { title: 'Status', key: 'status', sortable: true },
    { title: 'Data', key: 'created_at', sortable: true },
    { title: 'Ações', key: 'actions', sortable: false, align: 'end' as const }
  ]

  if (props.isStaff) {
    return [
      { title: 'Solicitante', key: 'requester', sortable: true },
      ...base
    ]
  }

  return base
})

const filteredDonations = computed(() => {
  if (!props.isStaff) return props.donations

  // Filter by tab
  const statusMap: Record<string, string[]> = {
    'pending_approval': ['pending_approval'],
    'pending_proof': ['approved', 'proof_attached'],
    'completed': ['completed', 'rejected']
  }

  const statuses = statusMap[currentTab.value] || []
  return props.donations.filter(d => statuses.includes(d.status))
})

// Methods
function getUserInitials(name: string): string {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
  }
  return name.charAt(0).toUpperCase()
}

function formatCurrency(value: number | string): string {
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(numValue || 0)
}

function formatDate(dateString: string): string {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR')
}

function formatDateTime(dateTimeString: string): string {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleString('pt-BR')
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    'pending_approval': 'warning',
    'approved': 'info',
    'rejected': 'error',
    'proof_attached': 'purple',
    'completed': 'success'
  }
  return colors[status] || 'grey'
}

function handleAmountInput(event: any) {
  const value = event.target.value
  const numericValue = value.replace(/[^\d]/g, '')

  if (!numericValue) {
    formattedAmount.value = ''
    formData.value.amount = 0
    return
  }

  const floatValue = parseFloat(numericValue) / 100
  formData.value.amount = floatValue
  formattedAmount.value = floatValue.toFixed(2).replace('.', ',')
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = { recipient: '', amount: 0, reason: '' }
  formattedAmount.value = ''
  showFormDialog.value = true
}

function openEditDialog(donation: any) {
  isEditing.value = true
  selectedDonation.value = donation
  formData.value = {
    recipient: donation.recipient,
    amount: donation.amount,
    reason: donation.reason
  }
  formattedAmount.value = parseFloat(donation.amount).toFixed(2).replace('.', ',')
  showFormDialog.value = true
}

function closeFormDialog() {
  showFormDialog.value = false
  selectedDonation.value = null
  formData.value = { recipient: '', amount: 0, reason: '' }
  formattedAmount.value = ''
}

async function saveDonation() {
  saving.value = true

  try {
    const endpoint = isEditing.value
      ? `/api/finance/donations/${selectedDonation.value.id}/`
      : '/api/finance/donations/'

    const method = isEditing.value ? 'PUT' : 'POST'

    const response = await fetch(endpoint, {
      method,
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Erro ao salvar solicitação')
    }

    successMessage.value = isEditing.value
      ? 'Solicitação atualizada com sucesso!'
      : 'Solicitação criada com sucesso!'
    showSuccess.value = true
    closeFormDialog()
    emit('refresh')
  } catch (err: any) {
    errorMessage.value = err.message
    showError.value = true
  } finally {
    saving.value = false
  }
}

function confirmDelete(donation: any) {
  selectedDonation.value = donation
  showDeleteDialog.value = true
}

async function deleteDonation() {
  deleting.value = true

  try {
    const response = await fetch(`/api/finance/donations/${selectedDonation.value.id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) throw new Error('Erro ao excluir solicitação')

    successMessage.value = 'Solicitação excluída com sucesso!'
    showSuccess.value = true
    showDeleteDialog.value = false
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao excluir solicitação'
    showError.value = true
  } finally {
    deleting.value = false
  }
}

async function approveDonation(donation: any) {
  try {
    const response = await fetch(`/api/finance/donations/${donation.id}/approve/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) throw new Error('Erro ao aprovar solicitação')

    successMessage.value = 'Solicitação aprovada com sucesso!'
    showSuccess.value = true
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao aprovar solicitação'
    showError.value = true
  }
}

function openRejectDialog(donation: any) {
  selectedDonation.value = donation
  rejectionReason.value = ''
  showRejectDialog.value = true
}

async function rejectDonation() {
  rejecting.value = true

  try {
    const response = await fetch(`/api/finance/donations/${selectedDonation.value.id}/reject/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rejection_reason: rejectionReason.value })
    })

    if (!response.ok) throw new Error('Erro ao rejeitar solicitação')

    successMessage.value = 'Solicitação rejeitada'
    showSuccess.value = true
    showRejectDialog.value = false
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao rejeitar solicitação'
    showError.value = true
  } finally {
    rejecting.value = false
  }
}

function openAttachProofDialog(donation: any) {
  selectedDonation.value = donation
  proofFile.value = null
  showAttachProofDialog.value = true
}

async function attachProof() {
  if (!proofFile.value) return

  attachingProof.value = true

  try {
    const formData = new FormData()
    formData.append('proof_document', proofFile.value)

    const response = await fetch(`/api/finance/donations/${selectedDonation.value.id}/attach_proof/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`
      },
      body: formData
    })

    if (!response.ok) throw new Error('Erro ao anexar comprovante')

    successMessage.value = 'Comprovante anexado com sucesso!'
    showSuccess.value = true
    showAttachProofDialog.value = false
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao anexar comprovante'
    showError.value = true
  } finally {
    attachingProof.value = false
  }
}

// ========== REGRESSÃO DE ETAPAS ==========

async function unapproveDonation(donation: any) {
  if (!confirm(`Deseja realmente desaprovar a solicitação de ${donation.recipient}? Ela voltará para "Pendente de Aprovação".`)) {
    return
  }

  try {
    const response = await fetch(`/api/finance/donations/${donation.id}/unapprove/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) throw new Error('Erro ao desaprovar solicitação')

    successMessage.value = 'Solicitação desaprovada. Status voltou para Pendente.'
    showSuccess.value = true
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao desaprovar solicitação'
    showError.value = true
  }
}

async function removeProof(donation: any) {
  if (!confirm(`Deseja remover o comprovante de ${donation.recipient}? O status voltará para "Aprovado".`)) {
    return
  }

  try {
    const response = await fetch(`/api/finance/donations/${donation.id}/remove_proof/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) throw new Error('Erro ao remover comprovante')

    successMessage.value = 'Comprovante removido. Status voltou para Aprovado.'
    showSuccess.value = true
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao remover comprovante'
    showError.value = true
  }
}

async function reopenDonation(donation: any) {
  if (!confirm(`Deseja reabrir a solicitação de ${donation.recipient}? Ela voltará para "Pendente de Aprovação".`)) {
    return
  }

  try {
    const response = await fetch(`/api/finance/donations/${donation.id}/reopen/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) throw new Error('Erro ao reabrir solicitação')

    successMessage.value = 'Solicitação reaberta. Status voltou para Pendente.'
    showSuccess.value = true
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao reabrir solicitação'
    showError.value = true
  }
}

async function completeDonation(donation: any) {
  try {
    const response = await fetch(`/api/finance/donations/${donation.id}/complete/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) throw new Error('Erro ao concluir doação')

    successMessage.value = 'Doação concluída com sucesso!'
    showSuccess.value = true
    emit('refresh')
  } catch (err) {
    errorMessage.value = 'Erro ao concluir doação'
    showError.value = true
  }
}

function viewDetails(donation: any) {
  selectedDonation.value = donation
  showDetailsDialog.value = true
}
</script>

<style scoped>
.v-data-table {
  border-radius: 0;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

<style>
/* Global tooltip styles for high contrast accessibility (WCAG 2.1 AA) */
.v-tooltip .v-overlay__content {
  background-color: #212121 !important;
  color: #FFFFFF !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  padding: 8px 12px !important;
  border-radius: 4px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}
</style>
