<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          <v-icon icon="mdi-account-group" class="mr-2" />
          Membros
        </h1>
        <p class="text-body-2 text-medium-emphasis">
          Gerencie todos os membros da plataforma ORBE
        </p>
      </div>

      <v-btn
        color="primary"
        prepend-icon="mdi-account-plus"
        size="large"
        @click="showInviteDialog = true"
      >
        Convidar Membro
      </v-btn>
    </div>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card rounded="lg" elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-caption text-medium-emphasis mb-1">Total de Membros</div>
                <div class="text-h5 font-weight-bold text-primary">
                  {{ stats.overview?.total_members || 0 }}
                </div>
              </div>
              <v-avatar color="primary" variant="tonal" size="48">
                <v-icon icon="mdi-account-group" size="28" />
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card rounded="lg" elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-caption text-medium-emphasis mb-1">Membros Ativos</div>
                <div class="text-h5 font-weight-bold text-success">
                  {{ stats.overview?.active_members || 0 }}
                </div>
              </div>
              <v-avatar color="success" variant="tonal" size="48">
                <v-icon icon="mdi-account-check" size="28" />
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card rounded="lg" elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-caption text-medium-emphasis mb-1">Com Mensalidades Atrasadas</div>
                <div class="text-h5 font-weight-bold text-error">
                  {{ stats.financial?.members_with_overdue || 0 }}
                </div>
              </div>
              <v-avatar color="error" variant="tonal" size="48">
                <v-icon icon="mdi-alert-circle" size="28" />
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card rounded="lg" elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-caption text-medium-emphasis mb-1">Novos (30 dias)</div>
                <div class="text-h5 font-weight-bold text-info">
                  {{ stats.overview?.recent_registrations_30d || 0 }}
                </div>
              </div>
              <v-avatar color="info" variant="tonal" size="48">
                <v-icon icon="mdi-account-plus-outline" size="28" />
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters and Search -->
    <v-card rounded="lg" elevation="2" class="mb-6">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-text-field
              v-model="filters.search"
              prepend-inner-icon="mdi-magnify"
              label="Buscar por nome ou email"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              @update:model-value="debouncedSearch"
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-select
              v-model="filters.role"
              :items="roleOptions"
              label="Filtrar por Role"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              @update:model-value="loadMembers"
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Filtrar por Status"
              variant="outlined"
              density="comfortable"
              clearable
              hide-details
              @update:model-value="loadMembers"
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-checkbox
              v-model="filters.has_overdue"
              label="Apenas com atrasos"
              density="comfortable"
              hide-details
              @update:model-value="loadMembers"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Members Table -->
    <v-card rounded="lg" elevation="2">
      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="members"
          :loading="loading"
          :items-per-page="25"
          loading-text="Carregando membros..."
          no-data-text="Nenhum membro encontrado"
          class="elevation-0"
        >
          <!-- Member Name -->
          <template #item.full_name="{ item }">
            <div class="d-flex align-center py-3">
              <v-avatar color="primary" size="40" class="mr-3">
                <span class="text-white font-weight-bold">
                  {{ getInitials(item.full_name) }}
                </span>
              </v-avatar>
              <div>
                <div class="font-weight-medium">{{ item.full_name }}</div>
                <div class="text-caption text-medium-emphasis">{{ item.email }}</div>
              </div>
            </div>
          </template>

          <!-- Role -->
          <template #item.role="{ item }">
            <v-chip
              :color="getRoleColor(item.role)"
              size="small"
              variant="tonal"
            >
              {{ item.role_display }}
            </v-chip>
          </template>

          <!-- Status -->
          <template #item.is_active="{ item }">
            <v-chip
              :color="item.is_active ? 'success' : 'error'"
              size="small"
              variant="tonal"
            >
              <v-icon
                :icon="item.is_active ? 'mdi-check-circle' : 'mdi-close-circle'"
                size="16"
                class="mr-1"
              />
              {{ item.is_active ? 'Ativo' : 'Inativo' }}
            </v-chip>
          </template>

          <!-- Financial Summary -->
          <template #item.financial="{ item }">
            <div class="py-2">
              <div class="text-caption text-medium-emphasis mb-1">
                Total Contribuído:
              </div>
              <div class="font-weight-bold text-success">
                R$ {{ formatCurrency(item.financial_summary?.total_contributed || 0) }}
              </div>
              <div class="text-caption text-medium-emphasis mt-1">
                <v-chip
                  v-if="item.financial_summary?.membership.overdue > 0"
                  color="error"
                  size="x-small"
                  variant="tonal"
                  class="mr-1"
                >
                  {{ item.financial_summary.membership.overdue }} atrasadas
                </v-chip>
                <v-chip
                  v-if="item.financial_summary?.membership.pending > 0"
                  color="warning"
                  size="x-small"
                  variant="tonal"
                >
                  {{ item.financial_summary.membership.pending }} pendentes
                </v-chip>
              </div>
            </div>
          </template>

          <!-- Registration Date -->
          <template #item.date_joined="{ item }">
            <div class="text-body-2">
              {{ formatDate(item.date_joined) }}
            </div>
          </template>

          <!-- Actions -->
          <template #item.actions="{ item }">
            <div class="d-flex gap-2">
              <v-btn
                icon="mdi-eye"
                size="small"
                variant="text"
                color="primary"
                @click="viewMember(item)"
              >
                <v-icon icon="mdi-eye" />
                <v-tooltip activator="parent" location="top">Ver Detalhes</v-tooltip>
              </v-btn>

              <v-btn
                icon="mdi-pencil"
                size="small"
                variant="text"
                color="info"
                @click="editMember(item)"
              >
                <v-icon icon="mdi-pencil" />
                <v-tooltip activator="parent" location="top">Editar Role</v-tooltip>
              </v-btn>

              <v-btn
                :icon="item.is_active ? 'mdi-account-off' : 'mdi-account-check'"
                size="small"
                variant="text"
                :color="item.is_active ? 'error' : 'success'"
                @click="toggleActive(item)"
              >
                <v-icon :icon="item.is_active ? 'mdi-account-off' : 'mdi-account-check'" />
                <v-tooltip activator="parent" location="top">
                  {{ item.is_active ? 'Desativar' : 'Ativar' }}
                </v-tooltip>
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Member Detail Dialog -->
    <v-dialog v-model="showDetailDialog" max-width="900" persistent>
      <v-card v-if="selectedMember" rounded="lg">
        <v-card-title class="bg-primary text-white pa-6">
          <div class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <v-avatar color="white" size="56" class="mr-4">
                <span class="text-primary font-weight-bold text-h6">
                  {{ getInitials(selectedMember.full_name) }}
                </span>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ selectedMember.full_name }}</div>
                <div class="text-body-2 text-white text-opacity-80">
                  {{ selectedMember.email }}
                </div>
              </div>
            </div>
            <v-btn icon="mdi-close" variant="text" color="white" @click="showDetailDialog = false" />
          </div>
        </v-card-title>

        <v-card-text class="pa-6">
          <v-tabs v-model="detailTab" color="primary" class="mb-6">
            <v-tab value="info">Informações</v-tab>
            <v-tab value="financial">Financeiro</v-tab>
            <v-tab value="cases">Casos de Assistência</v-tab>
          </v-tabs>

          <v-window v-model="detailTab">
            <!-- Info Tab -->
            <v-window-item value="info">
              <v-row>
                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">Role</div>
                    <v-chip :color="getRoleColor(selectedMember.role)" variant="tonal">
                      {{ selectedMember.role_display }}
                    </v-chip>
                  </div>

                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">Status</div>
                    <v-chip
                      :color="selectedMember.is_active ? 'success' : 'error'"
                      variant="tonal"
                    >
                      {{ selectedMember.is_active ? 'Ativo' : 'Inativo' }}
                    </v-chip>
                  </div>

                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">Método de Registro</div>
                    <div class="text-body-1">{{ selectedMember.registration_method || 'N/A' }}</div>
                  </div>

                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">Data de Cadastro</div>
                    <div class="text-body-1">{{ formatDate(selectedMember.date_joined) }}</div>
                  </div>
                </v-col>

                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">Telefone</div>
                    <div class="text-body-1">{{ selectedMember.profile?.phone || 'N/A' }}</div>
                  </div>

                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">Cidade/Estado</div>
                    <div class="text-body-1">
                      {{ selectedMember.profile?.city || 'N/A' }}, {{ selectedMember.profile?.state || 'N/A' }}
                    </div>
                  </div>

                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">País</div>
                    <div class="text-body-1">{{ selectedMember.profile?.country || 'N/A' }}</div>
                  </div>

                  <div class="mb-4">
                    <div class="text-caption text-medium-emphasis mb-1">Dia de Vencimento</div>
                    <div class="text-body-1">
                      Dia {{ selectedMember.profile?.membership_due_day || 10 }} de cada mês
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-window-item>

            <!-- Financial Tab -->
            <v-window-item value="financial">
              <div v-if="memberDetail">
                <!-- Financial Summary -->
                <v-row class="mb-6">
                  <v-col cols="12" md="4">
                    <v-card variant="tonal" color="primary">
                      <v-card-text>
                        <div class="text-caption mb-1">Total Contribuído</div>
                        <div class="text-h5 font-weight-bold">
                          R$ {{ formatCurrency(memberDetail.financial_summary?.total_contributed || 0) }}
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="4">
                    <v-card variant="tonal" color="success">
                      <v-card-text>
                        <div class="text-caption mb-1">Mensalidades Pagas</div>
                        <div class="text-h5 font-weight-bold">
                          {{ memberDetail.financial_summary?.paid_fees || 0 }} / {{ memberDetail.financial_summary?.total_fees || 0 }}
                        </div>
                        <div class="text-caption mt-1">
                          R$ {{ formatCurrency(memberDetail.financial_summary?.total_fees_amount || 0) }}
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="4">
                    <v-card variant="tonal" color="info">
                      <v-card-text>
                        <div class="text-caption mb-1">Doações</div>
                        <div class="text-h5 font-weight-bold">
                          {{ memberDetail.financial_summary?.total_donations || 0 }}
                        </div>
                        <div class="text-caption mt-1">
                          R$ {{ formatCurrency(memberDetail.financial_summary?.total_donations_amount || 0) }}
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>

                <!-- Membership Fees History -->
                <div class="mb-6">
                  <h3 class="text-h6 font-weight-bold mb-4">Histórico de Mensalidades (12 meses)</h3>
                  <v-table>
                    <thead>
                      <tr>
                        <th>Competência</th>
                        <th>Valor</th>
                        <th>Vencimento</th>
                        <th>Status</th>
                        <th>Data de Pagamento</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="fee in memberDetail.membership_fees" :key="fee.id">
                        <td>{{ formatMonth(fee.competency_month) }}</td>
                        <td>R$ {{ formatCurrency(fee.amount) }}</td>
                        <td>{{ formatDate(fee.due_date) }}</td>
                        <td>
                          <v-chip
                            :color="getStatusColor(fee.status)"
                            size="small"
                            variant="tonal"
                          >
                            {{ getStatusLabel(fee.status) }}
                          </v-chip>
                        </td>
                        <td>{{ fee.paid_at ? formatDate(fee.paid_at) : '-' }}</td>
                      </tr>
                    </tbody>
                  </v-table>
                  <div v-if="!memberDetail.membership_fees || memberDetail.membership_fees.length === 0" class="text-center text-medium-emphasis py-6">
                    Nenhuma mensalidade registrada
                  </div>
                </div>

                <!-- Donations History -->
                <div>
                  <h3 class="text-h6 font-weight-bold mb-4">Histórico de Doações (últimas 10)</h3>
                  <v-table>
                    <thead>
                      <tr>
                        <th>Data</th>
                        <th>Valor</th>
                        <th>Mensagem</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="donation in memberDetail.donations" :key="donation.id">
                        <td>{{ formatDate(donation.donated_at) }}</td>
                        <td>{{ donation.amount ? `R$ ${formatCurrency(donation.amount)}` : 'Anônimo' }}</td>
                        <td>{{ donation.message || '-' }}</td>
                      </tr>
                    </tbody>
                  </v-table>
                  <div v-if="!memberDetail.donations || memberDetail.donations.length === 0" class="text-center text-medium-emphasis py-6">
                    Nenhuma doação registrada
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-12">
                <v-progress-circular indeterminate color="primary" />
              </div>
            </v-window-item>

            <!-- Cases Tab -->
            <v-window-item value="cases">
              <div v-if="memberDetail">
                <div v-if="memberDetail.assistance_cases && memberDetail.assistance_cases.length > 0">
                  <v-card
                    v-for="caseItem in memberDetail.assistance_cases"
                    :key="caseItem.id"
                    class="mb-4"
                    variant="outlined"
                  >
                    <v-card-text>
                      <div class="d-flex align-center justify-space-between mb-2">
                        <div class="text-h6 font-weight-bold">{{ caseItem.title }}</div>
                        <v-chip
                          :color="getCaseStatusColor(caseItem.status)"
                          size="small"
                          variant="tonal"
                        >
                          {{ caseItem.status }}
                        </v-chip>
                      </div>
                      <div class="d-flex align-center gap-4 text-caption text-medium-emphasis">
                        <div>
                          <v-icon icon="mdi-currency-usd" size="16" class="mr-1" />
                          R$ {{ formatCurrency(caseItem.total_value) }}
                        </div>
                        <div>
                          <v-icon icon="mdi-calendar" size="16" class="mr-1" />
                          {{ formatDate(caseItem.created_at) }}
                        </div>
                        <div v-if="caseItem.approved_at">
                          <v-icon icon="mdi-check-circle" size="16" class="mr-1" />
                          Aprovado em {{ formatDate(caseItem.approved_at) }}
                        </div>
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
                <div v-else class="text-center text-medium-emphasis py-12">
                  Nenhum caso de assistência registrado
                </div>
              </div>
              <div v-else class="text-center py-12">
                <v-progress-circular indeterminate color="primary" />
              </div>
            </v-window-item>
          </v-window>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Edit Role Dialog -->
    <v-dialog v-model="showEditDialog" max-width="500" persistent>
      <v-card v-if="selectedMember" rounded="lg">
        <v-card-title class="bg-primary text-white pa-6">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-h5 font-weight-bold">Editar Role</div>
              <div class="text-body-2 text-white text-opacity-80">
                {{ selectedMember.full_name }}
              </div>
            </div>
            <v-btn icon="mdi-close" variant="text" color="white" @click="showEditDialog = false" />
          </div>
        </v-card-title>

        <v-card-text class="pa-6">
          <v-select
            v-model="editForm.role"
            :items="roleOptions"
            label="Nova Role"
            variant="outlined"
            prepend-inner-icon="mdi-shield-account"
          />
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="showEditDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="flat" :loading="updating" @click="updateRole">
            Salvar
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
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { apiService } from '@/services/api'

const authStore = useAuthStore()

// State
const loading = ref(false)
const updating = ref(false)
const members = ref<any[]>([])
const stats = ref<any>({})
const selectedMember = ref<any>(null)
const memberDetail = ref<any>(null)
const showDetailDialog = ref(false)
const showEditDialog = ref(false)
const showInviteDialog = ref(false)
const detailTab = ref('info')

// Toast
const showToast = ref(false)
const toastMessage = ref('')
const toastColor = ref('success')
const toastIcon = computed(() => toastColor.value === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle')

// Filters
const filters = ref({
  search: '',
  role: null,
  status: null,
  has_overdue: false
})

// Edit form
const editForm = ref({
  role: ''
})

// Table headers
const headers = [
  { title: 'Membro', key: 'full_name', sortable: true },
  { title: 'Role', key: 'role', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Financeiro', key: 'financial', sortable: false },
  { title: 'Cadastro', key: 'date_joined', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'end' }
]

// Options
const roleOptions = [
  { title: 'Membro', value: 'MEMBER' },
  { title: 'Diretoria', value: 'BOARD' },
  { title: 'Conselho Fiscal', value: 'FISCAL_COUNCIL' },
  { title: 'Super Admin', value: 'SUPER_ADMIN' }
]

const statusOptions = [
  { title: 'Ativo', value: 'true' },
  { title: 'Inativo', value: 'false' }
]

// Methods
async function loadStats() {
  try {
    const response = await apiService.get('/users/members/stats/')

    if (response.data) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

async function loadMembers() {
  try {
    loading.value = true

    const params = new URLSearchParams()
    if (filters.value.search) params.append('search', filters.value.search)
    if (filters.value.role) params.append('role', filters.value.role)
    if (filters.value.status) params.append('is_active', filters.value.status)
    if (filters.value.has_overdue) params.append('has_overdue', 'true')

    const query = params.toString()
    const endpoint = query ? `/users/members/?${query}` : '/users/members/'
    const response = await apiService.get(endpoint)

    if (response.data) {
      const data = response.data as any
      members.value = Array.isArray(data) ? data : data.results || []
    } else {
      members.value = []
    }
  } catch (error) {
    console.error('Error loading members:', error)
    showToastMessage('Erro ao carregar membros', 'error')
  } finally {
    loading.value = false
  }
}

async function viewMember(member: any) {
  selectedMember.value = member
  showDetailDialog.value = true
  detailTab.value = 'info'
  memberDetail.value = null

  // Load detailed member info
  try {
    const response = await apiService.get(`/users/members/${member.id}/`)

    if (response.data) {
      const detail = response.data as any
      memberDetail.value = {
        ...detail,
        membership_fees: Array.isArray(detail.membership_fees) ? detail.membership_fees : [],
        donations: Array.isArray(detail.donations) ? detail.donations : [],
        assistance_cases: Array.isArray(detail.assistance_cases) ? detail.assistance_cases : [],
      }
    } else {
      showToastMessage(response.error || 'Erro ao carregar detalhes do membro', 'error')
    }
  } catch (error) {
    console.error('Error loading member detail:', error)
    showToastMessage('Erro ao carregar detalhes do membro', 'error')
  }
}

function editMember(member: any) {
  selectedMember.value = member
  editForm.value.role = member.role
  showEditDialog.value = true
}

async function updateRole() {
  if (!selectedMember.value) return

  try {
    updating.value = true

    const response = await apiService.patch(`/users/members/${selectedMember.value.id}/update_role/`, {
      role: editForm.value.role
    })

    if (!response.error) {
      showToastMessage('Role atualizada com sucesso!', 'success')
      showEditDialog.value = false
      await loadMembers()
      await loadStats()
    } else {
      showToastMessage(response.error || 'Erro ao atualizar role', 'error')
    }
  } catch (error) {
    console.error('Error updating role:', error)
    showToastMessage('Erro ao atualizar role', 'error')
  } finally {
    updating.value = false
  }
}

async function toggleActive(member: any) {
  try {
    const response = await apiService.patch(`/users/members/${member.id}/toggle_active/`)

    if (response.data) {
      showToastMessage(response.data.message, 'success')
      await loadMembers()
      await loadStats()
    } else {
      showToastMessage(response.error || 'Erro ao atualizar status', 'error')
    }
  } catch (error) {
    console.error('Error toggling active:', error)
    showToastMessage('Erro ao atualizar status', 'error')
  }
}

function showToastMessage(message: string, color: string = 'success') {
  toastMessage.value = message
  toastColor.value = color
  showToast.value = true
}

// Debounced search
let searchTimeout: any = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadMembers()
  }, 500)
}

// Utility functions
function getInitials(name: string): string {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
}

function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    'SUPER_ADMIN': 'purple',
    'BOARD': 'primary',
    'FISCAL_COUNCIL': 'info',
    'MEMBER': 'secondary'
  }
  return colors[role] || 'grey'
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    'paid': 'success',
    'pending': 'warning',
    'overdue': 'error',
    'cancelled': 'grey'
  }
  return colors[status] || 'grey'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    'paid': 'Pago',
    'pending': 'Pendente',
    'overdue': 'Atrasado',
    'cancelled': 'Cancelado'
  }
  return labels[status] || status
}

function getCaseStatusColor(status: string): string {
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'error'
  if (status === 'completed') return 'info'
  return 'warning'
}

function formatCurrency(value: number): string {
  return value.toFixed(2).replace('.', ',')
}

function formatDate(date: string): string {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('pt-BR')
}

function formatMonth(date: string): string {
  if (!date) return '-'
  const d = new Date(date)
  return new Intl.DateTimeFormat('pt-BR', {
    month: 'long',
    year: 'numeric'
  }).format(d)
}

// Lifecycle
onMounted(() => {
  loadStats()
  loadMembers()
})
</script>

<style scoped>
.v-data-table :deep(th) {
  font-weight: 600 !important;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

.v-table :deep(th) {
  font-weight: 600 !important;
  background-color: rgba(var(--v-theme-primary), 0.05);
}
</style>
