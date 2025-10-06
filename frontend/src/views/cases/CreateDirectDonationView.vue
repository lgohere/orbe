<template>
  <v-container fluid class="pa-6">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <!-- Header -->
        <div class="mb-8">
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            class="mb-4"
            @click="$router.push('/cases')"
          >
            Voltar para Atendimentos
          </v-btn>

          <h1 class="text-h4 font-weight-bold text-primary mb-2">
            <v-icon icon="mdi-lightning-bolt" class="mr-2" />
            Nova Doação Direta
          </h1>
          <p class="text-body-1 text-medium-emphasis">
            Crie um caso de assistência já aprovado e concluído, sem necessidade de aprovação do Conselho Fiscal.
            Ideal para doações emergenciais a pessoas em vulnerabilidade (membros ou não-membros).
          </p>
        </div>

        <v-form ref="formRef" @submit.prevent="submitForm">
          <v-card rounded="lg" elevation="2" class="mb-6">
            <v-card-text class="pa-6">
              <!-- Step 1: Beneficiário -->
              <div class="mb-6">
                <h2 class="text-h6 font-weight-bold mb-4">
                  <v-icon icon="mdi-account" class="mr-2" color="primary" />
                  1. Beneficiário
                </h2>

                <v-text-field
                  v-model="form.beneficiary_name"
                  :rules="[rules.required, rules.minLength(3)]"
                  label="Nome completo do beneficiário"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  density="comfortable"
                  placeholder="Ex: João Silva"
                  hint="Nome da pessoa em situação de vulnerabilidade que receberá a assistência"
                  persistent-hint
                  class="mb-4"
                />

                <v-autocomplete
                  v-model="form.linked_member_ids"
                  :items="members"
                  :loading="loadingMembers"
                  :search="memberSearch"
                  item-title="full_name"
                  item-value="id"
                  label="Membros ORBE vinculados (opcional)"
                  prepend-inner-icon="mdi-account-multiple"
                  variant="outlined"
                  density="comfortable"
                  chips
                  multiple
                  closable-chips
                  hide-no-data
                  no-filter
                  :menu-props="{ maxHeight: 300 }"
                  placeholder="Digite pelo menos 3 letras para buscar..."
                  hint="Ex: membros que intermediaram, fizeram contato ou ajudaram"
                  persistent-hint
                  @update:search="onSearchMembers"
                >
                  <template #chip="{ props, item }">
                    <v-chip
                      v-bind="props"
                      closable
                      size="small"
                      color="primary"
                      variant="tonal"
                      class="ma-1"
                    >
                      <v-icon start size="small">mdi-account</v-icon>
                      {{ item.title }}
                    </v-chip>
                  </template>
                  <template #item="{ props, item }">
                    <v-list-item
                      v-bind="props"
                      :title="item.raw.full_name"
                      :subtitle="item.raw.email"
                    >
                      <template #prepend>
                        <v-avatar color="primary" size="36">
                          <span class="text-caption text-white font-weight-bold">
                            {{ getInitials(item.raw.full_name) }}
                          </span>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                  <template #no-data>
                    <v-list-item>
                      <v-list-item-title class="text-center text-medium-emphasis">
                        {{ memberSearch.length < 3 ? 'Digite pelo menos 3 letras para buscar' : 'Nenhum membro encontrado' }}
                      </v-list-item-title>
                    </v-list-item>
                  </template>
                </v-autocomplete>
              </div>

              <v-divider class="my-6" />

              <!-- Step 2: Informações do Caso -->
              <div class="mb-6">
                <h2 class="text-h6 font-weight-bold mb-4">
                  <v-icon icon="mdi-file-document" class="mr-2" color="primary" />
                  2. Informações do Atendimento
                </h2>

                <v-text-field
                  v-model="form.title"
                  :rules="[rules.required, rules.minLength(10)]"
                  label="Título do Atendimento"
                  prepend-inner-icon="mdi-format-title"
                  variant="outlined"
                  density="comfortable"
                  counter="200"
                  maxlength="200"
                  placeholder="Ex: Auxílio para compra de medicamentos"
                  class="mb-4"
                />

                <v-textarea
                  v-model="form.public_description"
                  :rules="[rules.required, rules.minLength(30)]"
                  label="Descrição Pública"
                  prepend-inner-icon="mdi-text"
                  variant="outlined"
                  rows="4"
                  counter="1000"
                  maxlength="1000"
                  placeholder="Descrição que será visível no feed para todos os membros. Descreva o motivo da assistência e como foi aplicada a doação."
                  hint="Esta descrição será exibida publicamente no feed"
                  persistent-hint
                  class="mb-4"
                />

                <v-textarea
                  v-model="form.internal_description"
                  :rules="[rules.required, rules.minLength(30)]"
                  label="Notas Internas (Admin/Diretoria)"
                  prepend-inner-icon="mdi-note-text"
                  variant="outlined"
                  rows="3"
                  counter="500"
                  maxlength="500"
                  placeholder="Notas internas sobre o caso (visível apenas para Admin e Diretoria)"
                  hint="Informações confidenciais sobre o caso"
                  persistent-hint
                  class="mb-4"
                />

                <v-text-field
                  v-model="formattedValue"
                  :rules="[rules.required, rules.positiveValue]"
                  label="Valor Total da Doação"
                  prepend-inner-icon="mdi-currency-usd"
                  prefix="R$"
                  variant="outlined"
                  density="comfortable"
                  type="text"
                  placeholder="0,00"
                  @input="formatCurrency"
                  @blur="addDecimalPlaces"
                />
              </div>

              <v-divider class="my-6" />

              <!-- Step 3: Comprovantes -->
              <div>
                <h2 class="text-h6 font-weight-bold mb-4">
                  <v-icon icon="mdi-paperclip" class="mr-2" color="primary" />
                  3. Comprovantes (Anexar após criar)
                </h2>

                <v-alert
                  type="info"
                  variant="tonal"
                  class="mb-4"
                  icon="mdi-information"
                >
                  <div class="text-body-2">
                    <strong>Importante:</strong> Após criar o caso, você será redirecionado para anexar:
                    <ul class="mt-2 ml-4">
                      <li>Comprovante de PIX ou transferência bancária</li>
                      <li>Fotos/documentos que comprovem a aplicação da doação</li>
                    </ul>
                  </div>
                </v-alert>
              </div>
            </v-card-text>

            <v-divider />

            <v-card-actions class="pa-6">
              <v-btn
                variant="text"
                size="large"
                @click="$router.push('/cases')"
              >
                Cancelar
              </v-btn>
              <v-spacer />
              <v-btn
                type="submit"
                color="primary"
                variant="flat"
                size="large"
                prepend-icon="mdi-check-circle"
                :loading="submitting"
              >
                Criar Doação Direta
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-form>
      </v-col>
    </v-row>

    <!-- Success Dialog -->
    <v-dialog v-model="showSuccessDialog" max-width="600" persistent>
      <v-card rounded="lg">
        <v-card-text class="pa-8 text-center">
          <v-avatar color="success" size="80" class="mb-4">
            <v-icon icon="mdi-check-circle" size="50" color="white" />
          </v-avatar>
          <h2 class="text-h5 font-weight-bold mb-3">Doação Criada com Sucesso!</h2>
          <p class="text-body-1 text-medium-emphasis mb-6">
            A doação direta para <strong>{{ form.beneficiary_name }}</strong> foi criada e já está com status <strong>Concluído</strong>.
            Agora você precisa anexar os comprovantes.
          </p>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn
            color="primary"
            variant="flat"
            size="large"
            @click="goToCaseDetail"
          >
            Anexar Comprovantes
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Toast -->
    <v-snackbar v-model="showToast" :color="toastColor" :timeout="3000" location="top">
      <div class="d-flex align-center">
        <v-icon :icon="toastIcon" class="mr-2" />
        {{ toastMessage }}
      </div>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form ref
const formRef = ref<any>(null)

// State
const submitting = ref(false)
const loadingMembers = ref(false)
const members = ref<any[]>([])
const memberSearch = ref('')
const createdCaseId = ref<number | null>(null)
const showSuccessDialog = ref(false)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// Toast
const showToast = ref(false)
const toastMessage = ref('')
const toastColor = ref('success')
const toastIcon = computed(() => toastColor.value === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle')

// Form data
const form = ref({
  beneficiary_name: '',
  linked_member_ids: [],
  title: '',
  public_description: '',
  internal_description: '',
  total_value: 0
})

const formattedValue = ref('')

// Validation rules
const rules = {
  required: (v: any) => !!v || 'Campo obrigatório',
  minLength: (min: number) => (v: string) => (v && v.length >= min) || `Mínimo de ${min} caracteres`,
  positiveValue: (v: any) => {
    const value = parseFloat(v.replace(',', '.'))
    return (value > 0) || 'O valor deve ser maior que zero'
  }
}

// Methods
async function loadMembers(search = '') {
  try {
    loadingMembers.value = true
    const params = new URLSearchParams({
      is_active: 'true',
      limit: '20'
    })
    if (search) {
      params.append('search', search)
    }

    const response = await fetch(`/api/users/members/autocomplete/?${params.toString()}`, {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (response.ok) {
      members.value = await response.json()
    } else {
      console.error('Failed to load members:', response.status)
      showToastMessage('Erro ao carregar membros', 'error')
    }
  } catch (error) {
    console.error('Error loading members:', error)
    showToastMessage('Erro ao carregar membros', 'error')
  } finally {
    loadingMembers.value = false
  }
}

function onSearchMembers(search: string | null) {
  memberSearch.value = search || ''

  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  // Only search with 3+ characters
  if (search && search.length >= 3) {
    // Debounce: wait 400ms before searching
    searchTimeout = setTimeout(() => {
      loadMembers(search)
    }, 400)
  } else {
    // Clear results if less than 3 characters
    members.value = []
  }
}

async function submitForm() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  try {
    submitting.value = true

    const response = await fetch('/api/assistance/cases/create_direct_donation/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })

    if (response.ok) {
      const data = await response.json()
      createdCaseId.value = data.case.id
      showSuccessDialog.value = true
    } else {
      const error = await response.json()
      const errorMessage = typeof error === 'object'
        ? Object.values(error).flat().join(', ')
        : 'Erro ao criar doação'
      showToastMessage(errorMessage, 'error')
    }
  } catch (error) {
    console.error('Error creating direct donation:', error)
    showToastMessage('Erro ao criar doação direta', 'error')
  } finally {
    submitting.value = false
  }
}

function goToCaseDetail() {
  if (createdCaseId.value) {
    router.push(`/cases/${createdCaseId.value}`)
  }
}

function showToastMessage(message: string, color: string = 'success') {
  toastMessage.value = message
  toastColor.value = color
  showToast.value = true
}

function formatCurrency(event: any) {
  let value = event.target.value
  value = value.replace(/[^\d,]/g, '')  // Only numbers and comma

  const parts = value.split(',')
  if (parts.length > 2) {
    value = parts[0] + ',' + parts.slice(1).join('')
  }

  if (parts.length === 2 && parts[1].length > 2) {
    value = parts[0] + ',' + parts[1].substring(0, 2)
  }

  formattedValue.value = value
  form.value.total_value = parseFloat(value.replace(',', '.')) || 0
}

function addDecimalPlaces() {
  if (!formattedValue.value) return

  let value = formattedValue.value

  if (!value.includes(',')) {
    value = value + ',00'
  } else {
    const parts = value.split(',')
    if (parts[1].length === 0) {
      value = parts[0] + ',00'
    } else if (parts[1].length === 1) {
      value = parts[0] + ',' + parts[1] + '0'
    }
  }

  formattedValue.value = value
  form.value.total_value = parseFloat(value.replace(',', '.')) || 0
}

function getInitials(name: string): string {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
}

// Lifecycle
onMounted(() => {
  // Members are loaded on-demand when user types 3+ characters
  // No initial load to avoid unnecessary API calls
})
</script>

<style scoped>
.v-card {
  transition: all 0.3s ease;
}

.v-divider {
  margin: 24px 0;
}

h2 .v-icon {
  vertical-align: middle;
}
</style>
