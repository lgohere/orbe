<template>
  <v-card>
    <v-card-title>
      <v-row align="center">
        <v-col cols="12" md="6">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-cash-multiple</v-icon>
            <span class="text-h6">{{ isStaff ? 'Gerenciar Mensalidades' : 'Minhas Mensalidades' }}</span>
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="d-flex justify-md-end">
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
          </div>
        </v-col>
      </v-row>
    </v-card-title>

    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="fees"
        :search="search"
        :items-per-page="10"
        class="elevation-0"
      >
        <!-- User Column (Only for Staff) -->
        <template v-if="isStaff" #item.user="{ item }">
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

        <!-- Competency Month Column -->
        <template #item.competency_month="{ item }">
          <span class="font-weight-medium">
            {{ formatMonth(item.competency_month) }}
          </span>
        </template>

        <!-- Amount Column -->
        <template #item.amount="{ item }">
          <span class="font-weight-bold text-primary">
            {{ formatCurrency(item.amount) }}
          </span>
        </template>

        <!-- Due Date Column -->
        <template #item.due_date="{ item }">
          <div>
            <div>{{ formatDate(item.due_date) }}</div>
            <div v-if="item.status === 'overdue'" class="text-caption text-error">
              {{ getDaysOverdue(item.due_date) }} dias de atraso
            </div>
          </div>
        </template>

        <!-- Status Column -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            variant="flat"
            size="small"
          >
            {{ getStatusLabel(item.status) }}
          </v-chip>
        </template>

        <!-- Paid At Column -->
        <template #item.paid_at="{ item }">
          <span v-if="item.paid_at" class="text-body-2">
            {{ formatDateTime(item.paid_at) }}
          </span>
          <span v-else class="text-grey">—</span>
        </template>

        <!-- Actions Column -->
        <template #item.actions="{ item }">
          <div class="d-flex gap-2">
            <v-btn
              v-if="isStaff && item.status !== 'paid'"
              icon="mdi-check"
              size="small"
              color="success"
              variant="text"
              @click="markAsPaid(item)"
            >
              <v-icon>mdi-check</v-icon>
              <v-tooltip activator="parent" location="top">
                Marcar como Pago
              </v-tooltip>
            </v-btn>
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="viewDetails(item)"
            >
              <v-icon>mdi-eye</v-icon>
              <v-tooltip activator="parent" location="top">
                Ver Detalhes
              </v-tooltip>
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card-text>

    <!-- Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="600">
      <v-card v-if="selectedFee">
        <v-card-title class="bg-primary text-white">
          <v-icon class="mr-2">mdi-cash-multiple</v-icon>
          Detalhes da Mensalidade
        </v-card-title>

        <v-card-text class="pt-4">
          <v-list density="comfortable">
            <v-list-item v-if="isStaff">
              <v-list-item-title class="text-caption text-grey">Membro</v-list-item-title>
              <v-list-item-subtitle class="text-body-1 font-weight-medium">
                {{ selectedFee.user_name }} ({{ selectedFee.user_email }})
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Mês de Competência</v-list-item-title>
              <v-list-item-subtitle class="text-body-1 font-weight-medium">
                {{ formatMonth(selectedFee.competency_month) }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Valor</v-list-item-title>
              <v-list-item-subtitle class="text-h6 text-primary font-weight-bold">
                {{ formatCurrency(selectedFee.amount) }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Data de Vencimento</v-list-item-title>
              <v-list-item-subtitle class="text-body-1">
                {{ formatDate(selectedFee.due_date) }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <v-list-item-title class="text-caption text-grey">Status</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip
                  :color="getStatusColor(selectedFee.status)"
                  variant="flat"
                  size="small"
                >
                  {{ getStatusLabel(selectedFee.status) }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedFee.paid_at">
              <v-list-item-title class="text-caption text-grey">Data de Pagamento</v-list-item-title>
              <v-list-item-subtitle class="text-body-1">
                {{ formatDateTime(selectedFee.paid_at) }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-list-item v-if="selectedFee.notes">
              <v-list-item-title class="text-caption text-grey">Observações</v-list-item-title>
              <v-list-item-subtitle class="text-body-2">
                {{ selectedFee.notes }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="showDetailsDialog = false">
            Fechar
          </v-btn>
          <v-btn
            v-if="isStaff && selectedFee.status !== 'paid'"
            color="success"
            variant="flat"
            prepend-icon="mdi-check"
            @click="markAsPaid(selectedFee); showDetailsDialog = false"
          >
            Marcar como Pago
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Props
const props = defineProps<{
  fees: any[]
  isStaff: boolean
}>()

// Emits
const emit = defineEmits<{
  refresh: []
}>()

// State
const search = ref('')
const showDetailsDialog = ref(false)
const selectedFee = ref<any>(null)

// Computed
const headers = computed(() => {
  const baseHeaders = [
    { title: 'Mês', key: 'competency_month', sortable: true },
    { title: 'Valor', key: 'amount', sortable: true },
    { title: 'Vencimento', key: 'due_date', sortable: true },
    { title: 'Status', key: 'status', sortable: true },
    { title: 'Pago em', key: 'paid_at', sortable: true },
    { title: 'Ações', key: 'actions', sortable: false, align: 'end' as const }
  ]

  if (props.isStaff) {
    return [
      { title: 'Membro', key: 'user', sortable: true },
      ...baseHeaders
    ]
  }

  return baseHeaders
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

function formatMonth(dateString: string): string {
  if (!dateString) return ''
  const date = new Date(dateString + 'T00:00:00')
  return date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
}

function formatDate(dateString: string): string {
  if (!dateString) return ''
  const date = new Date(dateString + 'T00:00:00')
  return date.toLocaleDateString('pt-BR')
}

function formatDateTime(dateTimeString: string): string {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleString('pt-BR')
}

function getDaysOverdue(dueDateString: string): number {
  const dueDate = new Date(dueDateString + 'T00:00:00')
  const today = new Date()
  const diff = today.getTime() - dueDate.getTime()
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    'paid': 'success',
    'pending': 'warning',
    'overdue': 'error'
  }
  return colors[status] || 'grey'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    'paid': 'Pago',
    'pending': 'Pendente',
    'overdue': 'Atrasado'
  }
  return labels[status] || status
}

function viewDetails(fee: any) {
  selectedFee.value = fee
  showDetailsDialog.value = true
}

async function markAsPaid(fee: any) {
  try {
    const response = await fetch(`/api/finance/fees/${fee.id}/mark_paid/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) throw new Error('Failed to mark fee as paid')

    // Refresh the list
    emit('refresh')
  } catch (err) {
    console.error('Error marking fee as paid:', err)
    alert('Erro ao marcar mensalidade como paga')
  }
}
</script>

<style scoped>
.v-data-table {
  border-radius: 0;
}
</style>
