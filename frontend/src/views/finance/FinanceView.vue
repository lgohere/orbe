<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold text-primary mb-2">Finanças</h1>
        <p class="text-body-1 text-grey-darken-1">
          Gerencie mensalidades e doações da ORBE
        </p>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p class="text-body-1 text-grey mt-4">Carregando dados financeiros...</p>
    </div>

    <!-- Error Alert -->
    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <!-- Financial Summary (Only for Board/Admin) -->
    <v-row v-if="!loading && isStaff">
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-caption text-grey mb-1">Total de Mensalidades</p>
                <p class="text-h5 font-weight-bold text-primary">
                  {{ formatCurrency(stats.totalFees) }}
                </p>
              </div>
              <v-icon color="primary" size="40">mdi-cash-multiple</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-caption text-grey mb-1">Mensalidades Pagas</p>
                <p class="text-h5 font-weight-bold text-success">
                  {{ formatCurrency(stats.paidFees) }}
                </p>
              </div>
              <v-icon color="success" size="40">mdi-check-circle</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-caption text-grey mb-1">Mensalidades Pendentes</p>
                <p class="text-h5 font-weight-bold text-warning">
                  {{ formatCurrency(stats.pendingFees) }}
                </p>
              </div>
              <v-icon color="warning" size="40">mdi-clock-alert</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-caption text-grey mb-1">Total de Doações</p>
                <p class="text-h5 font-weight-bold text-info">
                  {{ formatCurrency(stats.totalDonations) }}
                </p>
              </div>
              <v-icon color="info" size="40">mdi-hand-heart</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Main Content -->
    <v-row v-if="!loading">
      <!-- Tabs for Members, All Data for Staff -->
      <v-col cols="12">
        <v-tabs v-model="currentTab" color="primary">
          <v-tab value="membership">
            <v-icon start>mdi-cash-multiple</v-icon>
            {{ isStaff ? 'Todas as Mensalidades' : 'Minhas Mensalidades' }}
          </v-tab>
          <v-tab value="donations">
            <v-icon start>mdi-hand-heart</v-icon>
            {{ isStaff ? 'Todas as Doações' : 'Minhas Doações' }}
          </v-tab>
        </v-tabs>

        <v-window v-model="currentTab" class="mt-4">
          <!-- Membership Fees Tab -->
          <v-window-item value="membership">
            <MembershipFeesTable
              :fees="membershipFees"
              :is-staff="isStaff"
              @refresh="loadFinanceData"
            />
          </v-window-item>

          <!-- Donations Tab -->
          <v-window-item value="donations">
            <DonationsTable
              :donations="donations"
              :is-staff="isStaff"
              @refresh="loadFinanceData"
            />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import MembershipFeesTable from '@/components/finance/MembershipFeesTable.vue'
import DonationsTable from '@/components/finance/DonationsTable.vue'

const authStore = useAuthStore()

// State
const loading = ref(false)
const error = ref('')
const currentTab = ref('membership')

// Data
const membershipFees = ref<any[]>([])
const donations = ref<any[]>([])

interface FinancialStats {
  totalFees: number
  paidFees: number
  pendingFees: number
  totalDonations: number
}

const stats = ref<FinancialStats>({
  totalFees: 0,
  paidFees: 0,
  pendingFees: 0,
  totalDonations: 0
})

// Computed
const isStaff = computed(() => {
  const role = authStore.user?.role
  return role === 'SUPER_ADMIN' || role === 'BOARD' || role === 'FISCAL_COUNCIL'
})

// Methods
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value || 0)
}

async function loadFinanceData() {
  console.log('[FinanceView] Starting loadFinanceData...')
  loading.value = true
  error.value = ''

  try {
    console.log('[FinanceView] Calling Promise.all...')
    await Promise.all([
      loadMembershipFees(),
      loadDonations(),
      isStaff.value ? loadStats() : Promise.resolve()
    ])
    console.log('[FinanceView] All data loaded successfully')
  } catch (err: any) {
    console.error('[FinanceView] Error loading finance data:', err)
    error.value = 'Erro ao carregar dados financeiros'
  } finally {
    console.log('[FinanceView] Setting loading = false')
    loading.value = false
  }
}

async function loadMembershipFees() {
  try {
    const endpoint = isStaff.value
      ? '/api/finance/fees/'
      : '/api/finance/fees/my_fees/'

    const response = await fetch(endpoint, {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) throw new Error('Failed to load membership fees')

    const data = await response.json()
    // Handle both array response and paginated response
    membershipFees.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('Error loading membership fees:', err)
    throw err
  }
}

async function loadDonations() {
  try {
    const endpoint = isStaff.value
      ? '/api/finance/donations/'
      : '/api/finance/donations/my_donations/'

    const response = await fetch(endpoint, {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) throw new Error('Failed to load donations')

    const data = await response.json()
    // Handle both array response and paginated response
    donations.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('Error loading donations:', err)
    throw err
  }
}

async function loadStats() {
  try {
    // Calculate stats from membership fees
    const totalFees = membershipFees.value.reduce((sum, fee) => sum + parseFloat(fee.amount), 0)
    const paidFees = membershipFees.value
      .filter(fee => fee.status === 'paid')
      .reduce((sum, fee) => sum + parseFloat(fee.amount), 0)
    const pendingFees = membershipFees.value
      .filter(fee => fee.status === 'pending' || fee.status === 'overdue')
      .reduce((sum, fee) => sum + parseFloat(fee.amount), 0)

    // Get donation stats from API
    const response = await fetch('/api/finance/donations/stats/', {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) throw new Error('Failed to load donation stats')

    const donationStats = await response.json()

    stats.value = {
      totalFees,
      paidFees,
      pendingFees,
      totalDonations: donationStats.total_amount || 0
    }
  } catch (err) {
    console.error('Error loading stats:', err)
    // Stats are optional, don't throw
  }
}

// Lifecycle
onMounted(() => {
  loadFinanceData()
})
</script>

<style scoped>
.v-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
