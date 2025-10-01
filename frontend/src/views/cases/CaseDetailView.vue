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

          <div class="d-flex align-center justify-space-between flex-wrap">
            <div>
              <h1 class="text-h4 font-weight-bold text-primary mb-2">
                {{ caseData.title }}
              </h1>
              <v-chip :color="getStatusColor(caseData.status)" class="mr-2">
                {{ caseData.status_display }}
              </v-chip>
              <span class="text-body-2 text-grey">
                Criado em {{ formatDate(caseData.created_at) }}
              </span>
            </div>

            <!-- Actions -->
            <div class="d-flex gap-2 mt-2">
              <v-btn
                v-if="canEdit"
                color="primary"
                variant="outlined"
                prepend-icon="mdi-pencil"
                @click="$router.push(`/cases/${caseData.id}/edit`)"
              >
                Editar
              </v-btn>

              <v-btn
                v-if="canSubmit"
                color="primary"
                prepend-icon="mdi-send"
                @click="submitForApproval"
                :loading="submitting"
              >
                Enviar para Aprovação
              </v-btn>

              <v-btn
                v-if="canApprove"
                color="success"
                prepend-icon="mdi-check"
                @click="showApprovalDialog = true"
              >
                Aprovar
              </v-btn>

              <v-btn
                v-if="canApprove"
                color="error"
                prepend-icon="mdi-close"
                @click="showRejectionDialog = true"
              >
                Rejeitar
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
            <v-card-text class="text-body-1" style="white-space: pre-wrap;">
              {{ caseData.internal_description }}
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
                  <v-avatar color="grey-lighten-3">
                    <v-icon :color="attachment.is_image ? 'primary' : 'grey'">
                      {{ attachment.file_icon }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ attachment.file_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ attachment.file_type }} • {{ attachment.file_size_mb }} MB •
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

              <v-list-item v-if="caseData.approved_at">
                <v-list-item-title class="text-caption text-grey">Data de Aprovação</v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatDate(caseData.approved_at) }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider />

              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Última Atualização</v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatDate(caseData.updated_at) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card>

          <!-- Timeline Card (if has history) -->
          <v-card v-if="caseData.status !== 'draft'">
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-timeline-clock-outline</v-icon>
              Histórico
            </v-card-title>
            <v-timeline side="end" density="compact" class="pa-4">
              <v-timeline-item
                dot-color="success"
                size="small"
                icon="mdi-plus"
              >
                <div>
                  <div class="font-weight-bold">Caso Criado</div>
                  <div class="text-caption text-grey">{{ formatDate(caseData.created_at) }}</div>
                </div>
              </v-timeline-item>

              <v-timeline-item
                v-if="caseData.status !== 'draft'"
                dot-color="primary"
                size="small"
                icon="mdi-send"
              >
                <div>
                  <div class="font-weight-bold">Enviado para Aprovação</div>
                  <div class="text-caption text-grey">{{ formatDate(caseData.updated_at) }}</div>
                </div>
              </v-timeline-item>

              <v-timeline-item
                v-if="caseData.approved_at"
                dot-color="success"
                size="small"
                icon="mdi-check"
              >
                <div>
                  <div class="font-weight-bold">Aprovado</div>
                  <div class="text-caption text-grey">{{ formatDate(caseData.approved_at) }}</div>
                </div>
              </v-timeline-item>

              <v-timeline-item
                v-if="caseData.status === 'rejected'"
                dot-color="error"
                size="small"
                icon="mdi-close"
              >
                <div>
                  <div class="font-weight-bold">Rejeitado</div>
                  <div class="text-caption text-grey">{{ formatDate(caseData.updated_at) }}</div>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Approval Dialog -->
    <v-dialog v-model="showApprovalDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6 bg-success text-white">
          <v-icon class="mr-2">mdi-check-circle</v-icon>
          Aprovar Caso
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="text-body-1 mb-4">
            Tem certeza que deseja <strong>aprovar</strong> este caso de assistência?
          </p>
          <p class="text-body-2 text-grey">
            Após a aprovação, o caso será publicado no feed comunitário e se tornará visível para todos os membros.
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showApprovalDialog = false">Cancelar</v-btn>
          <v-btn color="success" @click="approveCase" :loading="approving">Confirmar Aprovação</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Rejection Dialog -->
    <v-dialog v-model="showRejectionDialog" max-width="600">
      <v-card>
        <v-card-title class="text-h6 bg-error text-white">
          <v-icon class="mr-2">mdi-close-circle</v-icon>
          Rejeitar Caso
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="text-body-1 mb-4">
            Por favor, explique o motivo da rejeição:
          </p>
          <v-textarea
            v-model="rejectionReason"
            label="Motivo da Rejeição"
            placeholder="Descreva detalhadamente o motivo da rejeição (mínimo 20 caracteres)..."
            variant="outlined"
            rows="4"
            :rules="[v => !!v || 'Motivo é obrigatório', v => v.length >= 20 || 'Mínimo de 20 caracteres']"
            counter
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showRejectionDialog = false">Cancelar</v-btn>
          <v-btn
            color="error"
            @click="rejectCase"
            :loading="rejecting"
            :disabled="!rejectionReason || rejectionReason.length < 20"
          >
            Confirmar Rejeição
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Success Snackbar -->
    <v-snackbar v-model="showSuccess" color="success" timeout="3000">
      {{ successMessage }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
const rejectionReason = ref('')
const showSuccess = ref(false)
const successMessage = ref('')

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
    successMessage.value = 'Caso aprovado com sucesso!'
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
    'approved': 'success',
    'rejected': 'error'
  }
  return colors[status] || 'grey'
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

// Lifecycle
onMounted(() => {
  loadCase()
})
</script>

<style scoped>
.gap-2 {
  gap: 0.5rem;
}
</style>
