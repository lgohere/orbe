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
      <v-col cols="12" md="4" class="d-flex align-center justify-end">
        <v-btn
          v-if="canCreateCases"
          color="primary"
          size="large"
          prepend-icon="mdi-plus"
          @click="$router.push('/cases/create')"
        >
          Novo Caso
        </v-btn>
      </v-col>
    </v-row>

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
              :items="statusOptions"
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

    <!-- Stats Cards (for Board/Fiscal Council) -->
    <v-row v-if="canSeeStats" class="mb-4">
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
                <div class="text-h5 font-weight-bold">{{ stats.pending }}</div>
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
              <v-avatar color="success-lighten-4" size="48" class="mr-3">
                <v-icon color="success" size="24">mdi-check-circle-outline</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.approved }}</div>
                <div class="text-caption text-grey">Aprovados</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar color="grey-lighten-3" size="48" class="mr-3">
                <v-icon color="grey-darken-2" size="24">mdi-pencil-outline</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ stats.draft }}</div>
                <div class="text-caption text-grey">Rascunhos</div>
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
        <h3 class="text-h6 mt-4 mb-2">Nenhum caso encontrado</h3>
        <p class="text-body-2 text-grey-darken-1 mb-4">
          {{ search ? 'Tente ajustar os filtros de busca' : 'Ainda não há casos cadastrados' }}
        </p>
        <v-btn
          v-if="canCreateCases && !search"
          color="primary"
          prepend-icon="mdi-plus"
          @click="$router.push('/cases/create')"
        >
          Criar Primeiro Caso
        </v-btn>
      </v-card-text>

      <!-- Cases Table/Cards -->
      <v-card-text v-else>
        <v-list lines="two">
          <v-list-item
            v-for="caseItem in cases"
            :key="caseItem.id"
            :to="`/cases/${caseItem.id}`"
            class="mb-2"
            border
            rounded
          >
            <template #prepend>
              <v-avatar :color="getStatusColor(caseItem.status)" size="48" class="mr-3">
                <v-icon :color="getStatusIconColor(caseItem.status)" size="24">
                  {{ getStatusIcon(caseItem.status) }}
                </v-icon>
              </v-avatar>
            </template>

            <v-list-item-title class="text-h6 font-weight-medium mb-1">
              {{ caseItem.title }}
            </v-list-item-title>

            <v-list-item-subtitle class="text-body-2">
              {{ truncateText(caseItem.public_description, 120) }}
            </v-list-item-subtitle>

            <template #append>
              <div class="d-flex flex-column align-end">
                <v-chip
                  :color="getStatusColor(caseItem.status)"
                  size="small"
                  class="mb-2"
                >
                  {{ caseItem.status_display }}
                </v-chip>
                <div class="text-caption text-grey">
                  <v-icon size="16" class="mr-1">mdi-currency-brl</v-icon>
                  {{ formatCurrency(caseItem.total_value) }}
                </div>
                <div class="text-caption text-grey">
                  <v-icon size="16" class="mr-1">mdi-paperclip</v-icon>
                  {{ caseItem.attachment_count }} anexo(s)
                </div>
              </div>
            </template>
          </v-list-item>
        </v-list>

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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

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
  pending: number
  approved: number
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
const stats = ref<Stats>({ total: 0, pending: 0, approved: 0, draft: 0 })

// Computed
const canCreateCases = computed(() => authStore.canCreateCases)
const canSeeStats = computed(() =>
  authStore.user?.role === 'BOARD' ||
  authStore.user?.role === 'FISCAL_COUNCIL' ||
  authStore.user?.role === 'SUPER_ADMIN'
)

// Options
const statusOptions = [
  { title: 'Todos', value: null },
  { title: 'Rascunho', value: 'draft' },
  { title: 'Pendente', value: 'pending_approval' },
  { title: 'Aprovado', value: 'approved' },
  { title: 'Rejeitado', value: 'rejected' }
]

const orderOptions = [
  { title: 'Mais Recentes', value: '-created_at' },
  { title: 'Mais Antigos', value: 'created_at' },
  { title: 'Maior Valor', value: '-total_value' },
  { title: 'Menor Valor', value: 'total_value' }
]

// Methods
async function loadCases() {
  loading.value = true
  try {
    const params = new URLSearchParams()

    if (search.value) params.append('search', search.value)
    if (statusFilter.value) params.append('status', statusFilter.value)
    if (orderBy.value) params.append('ordering', orderBy.value)
    params.append('page', currentPage.value.toString())

    const response = await fetch(`/api/assistance/cases/?${params}`, {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) throw new Error('Failed to load cases')

    const data: CasesResponse = await response.json()
    cases.value = data.results
    totalCount.value = data.count
    totalPages.value = Math.ceil(data.count / 20) // Assuming 20 per page

    // Load stats if user has permission
    if (canSeeStats.value) {
      await loadStats()
    }
  } catch (error) {
    console.error('Error loading cases:', error)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    // Load counts for each status
    const statuses = ['draft', 'pending_approval', 'approved', 'rejected']
    const counts = await Promise.all(
      statuses.map(async (status) => {
        const response = await fetch(`/api/assistance/cases/?status=${status}`, {
          headers: { 'Authorization': `Token ${authStore.token}` }
        })
        const data = await response.json()
        return data.count
      })
    )

    stats.value = {
      draft: counts[0],
      pending: counts[1],
      approved: counts[2],
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
    'approved': 'success',
    'rejected': 'error'
  }
  return colors[status] || 'grey'
}

function getStatusIconColor(status: string): string {
  const colors: Record<string, string> = {
    'draft': 'grey-darken-2',
    'pending_approval': 'warning-darken-2',
    'approved': 'success-darken-2',
    'rejected': 'error-darken-2'
  }
  return colors[status] || 'grey'
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    'draft': 'mdi-pencil-outline',
    'pending_approval': 'mdi-clock-outline',
    'approved': 'mdi-check-circle-outline',
    'rejected': 'mdi-close-circle-outline'
  }
  return icons[status] || 'mdi-file-document-outline'
}

function formatCurrency(value: string): string {
  const num = parseFloat(value)
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(num)
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Lifecycle
onMounted(() => {
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
</style>
