<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-4">
      <v-col cols="12">
        <v-btn
          variant="text"
          prepend-icon="mdi-arrow-left"
          @click="handleCancel"
          class="mb-2"
        >
          Voltar
        </v-btn>

        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          {{ isEditMode ? 'Editar Caso de Assistência' : 'Novo Caso de Assistência' }}
        </h1>
        <p class="text-body-1 text-grey-darken-1">
          {{ isEditMode ? 'Atualize as informações do caso' : 'Preencha os detalhes do caso de assistência' }}
        </p>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p class="text-body-1 text-grey mt-4">Carregando caso...</p>
    </div>

    <!-- Error Alert -->
    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <!-- Form -->
    <v-form v-if="!loading" ref="formRef" v-model="formValid" @submit.prevent="handleSubmit">
      <v-row>
        <!-- Main Form -->
        <v-col cols="12" md="8">
          <!-- Title -->
          <v-card class="mb-4">
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-text</v-icon>
              Título do Caso
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="formData.title"
                label="Título"
                placeholder="Ex: Auxílio Material Escolar - João Silva"
                variant="outlined"
                density="comfortable"
                :rules="[
                  v => !!v || 'Título é obrigatório',
                  v => v.length >= 10 || 'Título deve ter pelo menos 10 caracteres'
                ]"
                counter="200"
                maxlength="200"
                required
                autofocus
              />
            </v-card-text>
          </v-card>

          <!-- Public Description -->
          <v-card class="mb-4">
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-text-box-outline</v-icon>
              Descrição Pública
            </v-card-title>
            <v-card-subtitle class="pt-2">
              Esta descrição será visível para todos os membros após a aprovação
            </v-card-subtitle>
            <v-card-text>
              <v-textarea
                v-model="formData.public_description"
                label="Descrição Pública"
                placeholder="Descreva o caso de forma clara e objetiva. Esta informação será publicada no feed após aprovação."
                variant="outlined"
                rows="6"
                :rules="[
                  v => !!v || 'Descrição pública é obrigatória',
                  v => v.length >= 50 || 'Descrição deve ter pelo menos 50 caracteres'
                ]"
                counter
                required
              />
            </v-card-text>
          </v-card>

          <!-- Internal Description -->
          <v-card class="mb-4">
            <v-card-title class="text-h6 bg-warning-lighten-4">
              <v-icon class="mr-2">mdi-lock-outline</v-icon>
              Descrição Interna (Confidencial)
            </v-card-title>
            <v-card-subtitle class="pt-2">
              Informações confidenciais visíveis apenas para Conselho Diretor e Fiscal
            </v-card-subtitle>
            <v-card-text>
              <v-textarea
                v-model="formData.internal_description"
                label="Descrição Interna"
                placeholder="Detalhes confidenciais, informações sensíveis, notas sobre o beneficiário, justificativas internas..."
                variant="outlined"
                rows="6"
                counter
              />
              <v-alert type="info" density="compact" class="mt-2">
                <template #prepend>
                  <v-icon>mdi-information</v-icon>
                </template>
                Esta informação NÃO será publicada no feed público
              </v-alert>
            </v-card-text>
          </v-card>

          <!-- Total Value -->
          <v-card class="mb-4">
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-currency-brl</v-icon>
              Valor Total
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="formattedValue"
                label="Valor Total (R$)"
                placeholder="R$ 0,00"
                variant="outlined"
                density="comfortable"
                prefix="R$"
                :rules="[
                  v => !!v || 'Valor é obrigatório',
                  v => parseFloat(v.replace(/[^\d,]/g, '').replace(',', '.')) > 0 || 'Valor deve ser maior que zero'
                ]"
                @input="handleValueInput"
                required
              />
            </v-card-text>
          </v-card>

          <!-- Attachments -->
          <v-card>
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-paperclip</v-icon>
              Anexos ({{ attachments.length }})
            </v-card-title>
            <v-card-subtitle class="pt-2">
              Adicione documentos comprobatórios (PDF, JPG, PNG, DOC, DOCX - máx. 5MB cada)
            </v-card-subtitle>
            <v-card-text>
              <FileUploadZone
                v-model="attachments"
                :case-id="caseId"
                :disabled="!canUploadFiles"
              />
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Sidebar -->
        <v-col cols="12" md="4">
          <!-- Actions Card -->
          <v-card class="mb-4 sticky-top">
            <v-card-title class="text-h6 bg-primary text-white">
              <v-icon class="mr-2">mdi-content-save</v-icon>
              Ações
            </v-card-title>
            <v-card-text class="d-flex flex-column gap-3 pa-4">
              <!-- Save as Draft -->
              <v-btn
                color="grey-darken-1"
                variant="outlined"
                size="large"
                prepend-icon="mdi-content-save-outline"
                block
                :loading="saving"
                :disabled="!formValid"
                @click="saveAsDraft"
              >
                Salvar Rascunho
              </v-btn>

              <!-- Submit for Approval -->
              <v-btn
                color="primary"
                size="large"
                prepend-icon="mdi-send"
                block
                :loading="submitting"
                :disabled="!formValid"
                @click="submitForApproval"
              >
                {{ isEditMode ? 'Atualizar e Enviar' : 'Enviar para Aprovação' }}
              </v-btn>

              <!-- Cancel -->
              <v-btn
                variant="text"
                size="large"
                block
                @click="handleCancel"
              >
                Cancelar
              </v-btn>
            </v-card-text>
          </v-card>

          <!-- Help Card -->
          <v-card>
            <v-card-title class="text-h6 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-help-circle-outline</v-icon>
              Orientações
            </v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon size="small" color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    Título deve ser claro e objetivo (min. 10 caracteres)
                  </v-list-item-title>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon size="small" color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    Descrição pública deve ter no mínimo 50 caracteres
                  </v-list-item-title>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon size="small" color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    Valor total deve ser maior que zero
                  </v-list-item-title>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon size="small" color="warning">mdi-alert-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    Anexe documentos comprobatórios quando possível
                  </v-list-item-title>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon size="small" color="info">mdi-information</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    Rascunhos podem ser editados posteriormente
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-form>

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
import FileUploadZone from '@/components/cases/FileUploadZone.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const formRef = ref()
const formValid = ref(false)
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const error = ref('')
const showSuccess = ref(false)
const successMessage = ref('')
const caseId = ref<number | null>(null)
const attachments = ref<any[]>([])

interface FormData {
  title: string
  public_description: string
  internal_description: string
  total_value: number
}

const formData = ref<FormData>({
  title: '',
  public_description: '',
  internal_description: '',
  total_value: 0
})

const formattedValue = ref('')

// Computed
const isEditMode = computed(() => !!route.params.id)
const canUploadFiles = computed(() => !!caseId.value || isEditMode.value)

// Methods
async function loadCase() {
  if (!isEditMode.value) return

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
      } else if (response.status === 403) {
        error.value = 'Você não tem permissão para editar este caso'
      } else {
        error.value = 'Erro ao carregar caso'
      }
      return
    }

    const data = await response.json()

    // Check if case can be edited
    if (!data.can_be_edited) {
      error.value = `Casos com status "${data.status_display}" não podem ser editados`
      setTimeout(() => router.push(`/cases/${route.params.id}`), 2000)
      return
    }

    // Populate form
    formData.value = {
      title: data.title,
      public_description: data.public_description,
      internal_description: data.internal_description || '',
      total_value: parseFloat(data.total_value)
    }

    formattedValue.value = formatCurrency(data.total_value)
    caseId.value = data.id
    attachments.value = data.attachments || []
  } catch (err) {
    console.error('Error loading case:', err)
    error.value = 'Erro ao carregar caso'
  } finally {
    loading.value = false
  }
}

async function saveAsDraft() {
  if (!formValid.value) return

  saving.value = true
  error.value = ''

  try {
    const payload = {
      ...formData.value,
      status: 'draft'
    }

    const url = isEditMode.value
      ? `/api/assistance/cases/${route.params.id}/`
      : '/api/assistance/cases/'

    const method = isEditMode.value ? 'PATCH' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = extractErrorMessage(data)
      return
    }

    const data = await response.json()
    caseId.value = data.id

    successMessage.value = isEditMode.value
      ? 'Caso atualizado com sucesso!'
      : 'Rascunho salvo com sucesso!'
    showSuccess.value = true

    // If creating new case, update URL to edit mode
    if (!isEditMode.value) {
      router.replace(`/cases/${data.id}/edit`)
    }
  } catch (err) {
    console.error('Error saving draft:', err)
    error.value = 'Erro ao salvar rascunho'
  } finally {
    saving.value = false
  }
}

async function submitForApproval() {
  if (!formValid.value) return

  submitting.value = true
  error.value = ''

  try {
    // First save the case (if new or updated)
    const payload = {
      ...formData.value,
      status: 'pending_approval'
    }

    const url = isEditMode.value
      ? `/api/assistance/cases/${route.params.id}/`
      : '/api/assistance/cases/'

    const method = isEditMode.value ? 'PATCH' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = extractErrorMessage(data)
      return
    }

    const data = await response.json()

    successMessage.value = 'Caso enviado para aprovação com sucesso!'
    showSuccess.value = true

    // Redirect to case detail
    setTimeout(() => {
      router.push(`/cases/${data.id}`)
    }, 1500)
  } catch (err) {
    console.error('Error submitting case:', err)
    error.value = 'Erro ao enviar caso para aprovação'
  } finally {
    submitting.value = false
  }
}

function handleValueInput(event: any) {
  const value = event.target.value
  const numericValue = value.replace(/[^\d]/g, '')

  if (!numericValue) {
    formattedValue.value = ''
    formData.value.total_value = 0
    return
  }

  const floatValue = parseFloat(numericValue) / 100
  formData.value.total_value = floatValue
  formattedValue.value = floatValue.toFixed(2).replace('.', ',')
}

function formatCurrency(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toFixed(2).replace('.', ',')
}

function extractErrorMessage(errorData: any): string {
  if (typeof errorData === 'string') return errorData

  // Extract first error from validation errors
  const errors = []
  for (const key in errorData) {
    if (Array.isArray(errorData[key])) {
      errors.push(...errorData[key])
    } else {
      errors.push(errorData[key])
    }
  }

  return errors.length > 0 ? errors[0] : 'Erro ao processar requisição'
}

function handleCancel() {
  if (isEditMode.value && route.params.id) {
    router.push(`/cases/${route.params.id}`)
  } else {
    router.push('/cases')
  }
}

// Lifecycle
onMounted(() => {
  if (isEditMode.value) {
    loadCase()
  }
})
</script>

<style scoped>
.sticky-top {
  position: sticky;
  top: 16px;
}

.gap-3 {
  gap: 12px;
}
</style>
