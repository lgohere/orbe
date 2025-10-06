<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-4">
      <v-col cols="12" md="8">
        <h1 class="text-h4 font-weight-bold text-primary mb-2">Casos de Assistência</h1>
        <p class="text-body-1 text-grey-darken-1">
          Gestão de casos de assistência social da ORBE
        </p>
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center justify-end gap-2">
        <v-btn
          v-if="authStore.user?.role === 'SUPER_ADMIN'"
          color="success"
          size="large"
          prepend-icon="mdi-lightning-bolt"
          @click="$router.push('/cases/create-direct-donation')"
        >
          Doação Direta
        </v-btn>
      </v-col>
    </v-row>

    <!-- Tabs: Em Andamento / Concluídos -->
    <v-tabs v-model="activeTab" bg-color="transparent" color="primary" class="mb-4" @update:model-value="onTabChange">
      <v-tab value="in_progress">
        <v-icon class="mr-2">mdi-progress-clock</v-icon>
        Em Andamento
        <v-chip size="small" class="ml-2" color="warning">{{ stats.in_progress }}</v-chip>
      </v-tab>
      <v-tab value="completed">
        <v-icon class="mr-2">mdi-check-circle</v-icon>
        Concluídos
        <v-chip size="small" class="ml-2" color="success">{{ stats.completed }}</v-chip>
      </v-tab>
    </v-tabs>

    <!-- Filters & Search -->
    <v-card flat class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Buscar casos..."
              placeholder="Título ou descrição"
              variant="outlined"
              density="comfortable"
              clearable
              @update:model-value="debouncedSearch"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="statusFilter"
              :items="currentStatusOptions"
              label="Status"
              variant="outlined"
              density="comfortable"
              clearable
              @update:model-value="loadCases"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="orderBy"
              :items="orderOptions"
              label="Ordenar por"
              variant="outlined"
              density="comfortable"
              @update:model-value="loadCases"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Stats Cards (for Board/Fiscal Council/Admin) - Only for "In Progress" tab -->
    <v-row v-if="canSeeStats && activeTab === 'in_progress'" class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="grey-lighten-3" size="48" class="mr-3">
                <v-icon color="grey-darken-2" size="24">mdi-file-document-outline</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.total }}</div>
                <div class="text-caption text-grey">Total de Casos</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="warning-lighten-4" size="48" class="mr-3">
                <v-icon color="warning" size="24">mdi-clock-outline</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.pending_approval }}</div>
                <div class="text-caption text-grey">Pendentes</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="info-lighten-4" size="48" class="mr-3">
                <v-icon color="info" size="24">mdi-bank-transfer</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.awaiting_transfer }}</div>
                <div class="text-caption text-grey">Aguard. Transf.</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="purple-lighten-4" size="48" class="mr-3">
                <v-icon color="purple" size="24">mdi-camera</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.awaiting_member_proof }}</div>
                <div class="text-caption text-grey">Aguard. Comprov.</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Cases List -->
    <v-card flat>
      <!-- Loading State -->
      <v-card-text v-if="loading" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64" />
        <p class="text-body-1 text-grey mt-4">Carregando casos...</p>
      </v-card-text>

      <!-- Empty State -->
      <v-card-text v-else-if="!loading && cases.length === 0" class="text-center py-12">
        <v-icon size="80" color="grey-lighten-1">mdi-folder-open-outline</v-icon>
        <h3 class="text-h6 mt-4 mb-2">
          {{ activeTab === 'completed' ? 'Nenhum caso concluído' : 'Nenhum caso em andamento' }}
        </h3>
        <p class="text-body-2 text-grey-darken-1 mb-4">
          {{ search ? 'Tente ajustar os filtros de busca' : 'Ainda não há casos nesta categoria' }}
        </p>
        <v-btn
          v-if="canCreateCases && !search && activeTab === 'in_progress'"
          color="primary"
          prepend-icon="mdi-plus"
          @click="$router.push('/cases/create')"
        >
          Criar Primeiro Caso
        </v-btn>
      </v-card-text>

      <!-- Cases List - Grouped by Month/Year -->
      <v-card-text v-else>
        <div v-for="monthGroup in casesByMonth" :key="monthGroup.monthYear" class="mb-6">
          <!-- Month/Year Header -->
          <div class="d-flex align-center mb-3">
            <v-icon color="primary" class="mr-2">mdi-calendar-month</v-icon>
            <h2 class="text-h6 font-weight-bold text-primary text-capitalize">
              {{ monthGroup.label }}
            </h2>
            <v-chip size="small" class="ml-3" color="primary" variant="outlined">
              {{ monthGroup.cases.length }} caso(s)
            </v-chip>
          </div>

          <!-- Cases for this month -->
          <v-list lines="three">
            <v-list-item
              v-for="caseItem in monthGroup.cases"
              :key="caseItem.id"
              :to="`/cases/${caseItem.id}`"
              class="mb-3"
              border
              rounded
            >
              <template #prepend>
                <v-avatar :color="getStatusColor(caseItem.status)" size="56" class="mr-4">
                  <v-icon :color="getStatusIconColor(caseItem.status)" size="28">
                    {{ getStatusIcon(caseItem.status) }}
                  </v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="text-h6 font-weight-medium mb-1">
                {{ caseItem.title }}
              </v-list-item-title>

              <v-list-item-subtitle class="text-body-2 mb-2">
                {{ truncateText(caseItem.public_description, 120) }}
              </v-list-item-subtitle>

              <!-- Progress indicator for in-progress cases -->
              <div v-if="activeTab === 'in_progress'" class="mt-2">
                <v-progress-linear
                  :model-value="getProgressPercentage(caseItem.status)"
                  :color="getStatusColor(caseItem.status)"
                  height="6"
                  rounded
                />
                <div class="text-caption text-grey mt-1">
                  {{ getProgressLabel(caseItem.status) }}
                </div>
              </div>

              <template #append>
                <div class="d-flex flex-column align-end">
                  <v-chip
                    :color="getStatusColor(caseItem.status)"
                    size="small"
                    class="mb-2"
                  >
                    {{ caseItem.status_display }}
                  </v-chip>
                  <div class="text-caption text-grey mb-1">
                    <v-icon size="16" class="mr-1">mdi-currency-brl</v-icon>
                    R$ {{ Number(caseItem.total_value).toFixed(2) }}
                  </div>
                  <div class="text-caption text-grey">
                    <v-icon size="16" class="mr-1">mdi-paperclip</v-icon>
                    {{ caseItem.attachment_count }} anexo(s)
                  </div>
                </div>
              </template>
            </v-list-item>
          </v-list>
        </div>

        <!-- Pagination -->
        <v-pagination
          v-if="totalPages > 1"
          v-model="currentPage"
          :length="totalPages"
          :total-visible="7"
          class="mt-4"
          @update:model-value="loadCases"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { apiService } from '@/services/api'

interface Case {
  id: number
  title: string
  public_description: string
  total_value: string
  status: string
  status_display: string
  created_by: any
  created_at: string
  attachment_count: number
  can_be_edited: boolean
}

interface CasesResponse {
  count: number
  next: string | null
  previous: string | null
  results: Case[]
}

interface Stats {
  total: number
  pending_approval: number
  awaiting_bank_info: number
  awaiting_transfer: number
  awaiting_member_proof: number
  pending_validation: number
  completed: number
  in_progress: number
  draft: number
}

const authStore = useAuthStore()

// State
const cases = ref<Case[]>([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref<string | null>(null)
const orderBy = ref('-created_at')
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const activeTab = ref<'in_progress' | 'completed'>('in_progress')
const stats = ref<Stats>({
  total: 0,
  pending_approval: 0,
  awaiting_bank_info: 0,
  awaiting_transfer: 0,
  awaiting_member_proof: 0,
  pending_validation: 0,
  completed: 0,
  in_progress: 0,
  draft: 0
})

// Computed
const canCreateCases = computed(() => authStore.canCreateCases)
const canSeeStats = computed(() =>
  authStore.user?.role === 'BOARD' ||
  authStore.user?.role === 'FISCAL_COUNCIL' ||
  authStore.user?.role === 'SUPER_ADMIN'
)

// Group cases by month/year
const casesByMonth = computed(() => {
  const grouped = new Map<string, Case[]>()

  cases.value.forEach(caseItem => {
    const date = new Date(caseItem.created_at)
    const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`

    if (!grouped.has(monthYear)) {
      grouped.set(monthYear, [])
    }
    grouped.get(monthYear)!.push(caseItem)
  })

  // Sort by month/year descending (most recent first)
  return Array.from(grouped.entries())
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([monthYear, cases]) => ({
      monthYear,
      label: formatMonthYear(monthYear),
      cases
    }))
})

// Status options based on active tab
const currentStatusOptions = computed(() => {
  if (activeTab.value === 'completed') {
    return [
      { title: 'Todos Concluídos', value: null }
    ]
  }

  return [
    { title: 'Todos em Andamento', value: null },
    { title: 'Rascunho', value: 'draft' },
    { title: 'Pendente de Aprovação', value: 'pending_approval' },
    { title: 'Aguardando Dados Bancários', value: 'awaiting_bank_info' },
    { title: 'Aguardando Transferência', value: 'awaiting_transfer' },
    { title: 'Aguardando Comprovação', value: 'awaiting_member_proof' },
    { title: 'Pendente de Validação', value: 'pending_validation' },
    { title: 'Rejeitado', value: 'rejected' }
  ]
})

const orderOptions = [
  { title: 'Mais Recentes', value: '-created_at' },
  { title: 'Mais Antigos', value: 'created_at' },
  { title: 'Maior Valor', value: '-total_value' },
  { title: 'Menor Valor', value: 'total_value' }
]

// Methods
function onTabChange() {
  statusFilter.value = null
  currentPage.value = 1
  loadCases()
}

async function loadCases() {
  loading.value = true
  try {
    const params = new URLSearchParams()

    if (search.value) params.append('search', search.value)

    // Filter by tab
    if (activeTab.value === 'completed') {
      params.append('status', 'completed')
    } else {
      // In progress: exclude completed
      if (statusFilter.value) {
        params.append('status', statusFilter.value)
      } else {
        // Show all except completed
        params.append('exclude_status', 'completed')
      }
    }

    if (orderBy.value) params.append('ordering', orderBy.value)
    params.append('page', currentPage.value.toString())

    const response = await apiService.get<CasesResponse | { results: any[]; count: number }>(`/assistance/cases/?${params}`)

    if (!response.data) throw new Error(response.error || 'Failed to load cases')

    const data = response.data as CasesResponse
    cases.value = data.results
    totalCount.value = data.count
    totalPages.value = Math.ceil(data.count / 20)

    // Always load basic stats (in_progress and completed counts)
    await loadBasicStats()

    // Load detailed stats if user has permission
    if (canSeeStats.value) {
      await loadStats()
    }
  } catch (error) {
    console.error('Error loading cases:', error)
  } finally {
    loading.value = false
  }
}

async function loadBasicStats() {
  try {
    // Load in_progress count (all except completed)
    const inProgressResponse = await apiService.get<{ count: number }>(`/assistance/cases/?exclude_status=completed`)
    if (inProgressResponse.data) {
      stats.value.in_progress = inProgressResponse.data.count
    }

    // Load completed count
    const completedResponse = await apiService.get<{ count: number }>(`/assistance/cases/?status=completed`)
    if (completedResponse.data) {
      stats.value.completed = completedResponse.data.count
    }

    // Update total
    stats.value.total = stats.value.in_progress + stats.value.completed
  } catch (error) {
    console.error('Error loading basic stats:', error)
  }
}

async function loadStats() {
  try {
    const statuses = [
      'draft',
      'pending_approval',
      'awaiting_bank_info',
      'awaiting_transfer',
      'awaiting_member_proof',
      'pending_validation',
      'completed'
    ]

    const counts = await Promise.all(
      statuses.map(async (status) => {
        const response = await apiService.get<{ count: number }>(`/assistance/cases/?status=${status}`)
        return response.data?.count ?? 0
      })
    )

    stats.value = {
      draft: counts[0],
      pending_approval: counts[1],
      awaiting_bank_info: counts[2],
      awaiting_transfer: counts[3],
      awaiting_member_proof: counts[4],
      pending_validation: counts[5],
      completed: counts[6],
      in_progress: counts[0] + counts[1] + counts[2] + counts[3] + counts[4] + counts[5],
      total: counts.reduce((sum, count) => sum + count, 0)
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

let searchTimeout: number | null = null
function debouncedSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadCases()
  }, 500)
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    'draft': 'grey-lighten-2',
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

function getStatusIconColor(status: string): string {
  const colors: Record<string, string> = {
    'draft': 'grey-darken-2',
    'pending_approval': 'warning-darken-2',
    'awaiting_bank_info': 'blue-grey-darken-2',
    'awaiting_transfer': 'info-darken-2',
    'awaiting_member_proof': 'purple-darken-2',
    'pending_validation': 'deep-orange-darken-2',
    'completed': 'success-darken-2',
    'rejected': 'error-darken-2'
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

function getProgressPercentage(status: string): number {
  const progress: Record<string, number> = {
    'draft': 10,
    'pending_approval': 20,
    'awaiting_bank_info': 35,
    'awaiting_transfer': 50,
    'awaiting_member_proof': 70,
    'pending_validation': 85,
    'completed': 100
  }
  return progress[status] || 0
}

function getProgressLabel(status: string): string {
  const labels: Record<string, string> = {
    'draft': 'Passo 1 de 6: Rascunho',
    'pending_approval': 'Passo 2 de 6: Aguardando aprovação',
    'awaiting_bank_info': 'Passo 3 de 6: Membro deve informar dados bancários',
    'awaiting_transfer': 'Passo 4 de 6: Admin deve confirmar transferência',
    'awaiting_member_proof': 'Passo 5 de 6: Membro deve enviar comprovantes',
    'pending_validation': 'Passo 6 de 6: Admin validando comprovantes'
  }
  return labels[status] || ''
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

function formatMonthYear(monthYear: string): string {
  const [year, month] = monthYear.split('-')
  const date = new Date(parseInt(year), parseInt(month) - 1)

  return new Intl.DateTimeFormat('pt-BR', {
    month: 'long',
    year: 'numeric'
  }).format(date)
}

// Lifecycle
onMounted(() => {
  loadCases()
})

// Watch tab changes
watch(activeTab, () => {
  statusFilter.value = null
  currentPage.value = 1
  loadCases()
})
</script>

<style scoped>
.v-list-item {
  transition: all 0.2s ease;
}

.v-list-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Month/Year group styling */
.mb-6:not(:last-child) {
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 1.5rem;
}

/* Month header styling */
h2.text-capitalize {
  letter-spacing: 0.5px;
}
</style>
