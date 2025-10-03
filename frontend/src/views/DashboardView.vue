<template>
  <div>
    <!-- Welcome Header -->
    <div class="mb-8">
      <h1 class="text-h4 font-weight-bold mb-2">
        Bem-vindo, {{ authStore.user?.first_name }}! 👋
      </h1>
      <p class="text-body-1 text-medium-emphasis">
        {{ getWelcomeMessage() }}
      </p>
    </div>

    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col
        v-for="stat in stats"
        :key="stat.title"
        cols="12"
        sm="6"
        md="3"
      >
        <v-card
          class="stat-card"
          :color="stat.color"
          variant="flat"
          rounded="lg"
        >
          <v-card-text class="pa-6">
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-caption text-white text-opacity-80 mb-1">
                  {{ stat.title }}
                </div>
                <div class="text-h4 font-weight-bold text-white">
                  {{ stat.value }}
                </div>
                <div
                  v-if="stat.change"
                  class="text-caption text-white text-opacity-80 mt-1"
                >
                  <v-icon
                    :icon="stat.changePositive ? 'mdi-trending-up' : 'mdi-trending-down'"
                    size="small"
                    class="mr-1"
                  />
                  {{ stat.change }}
                </div>
              </div>
              <v-avatar
                :color="stat.iconBg"
                size="56"
              >
                <v-icon
                  :icon="stat.icon"
                  size="28"
                  color="white"
                />
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Main Content Grid -->
    <v-row>
      <!-- Left Column -->
      <v-col cols="12" md="8">
        <!-- Recent Activity -->
        <v-card rounded="lg" class="mb-6">
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon icon="mdi-clock-outline" class="mr-2" />
              <span class="text-h6">Atividades Recentes</span>
            </div>
            <v-btn
              variant="text"
              size="small"
              append-icon="mdi-chevron-right"
            >
              Ver todas
            </v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-0">
            <v-list lines="two">
              <v-list-item
                v-for="(activity, index) in recentActivities"
                :key="index"
                class="px-6"
              >
                <template v-slot:prepend>
                  <v-avatar :color="activity.color" size="40">
                    <v-icon :icon="activity.icon" color="white" />
                  </v-avatar>
                </template>
                <v-list-item-title class="font-weight-medium">
                  {{ activity.title }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ activity.description }}
                </v-list-item-subtitle>
                <template v-slot:append>
                  <div class="text-caption text-medium-emphasis">
                    {{ activity.time }}
                  </div>
                </template>
              </v-list-item>
            </v-list>

            <!-- Empty State -->
            <div v-if="recentActivities.length === 0" class="pa-12 text-center">
              <v-icon icon="mdi-inbox-outline" size="64" color="grey-lighten-1" class="mb-4" />
              <div class="text-h6 text-medium-emphasis mb-2">
                Nenhuma atividade recente
              </div>
              <div class="text-body-2 text-medium-emphasis">
                Suas atividades aparecerão aqui
              </div>
            </div>
          </v-card-text>
        </v-card>

        <!-- Upcoming Events / Tasks -->
        <v-card rounded="lg">
          <v-card-title class="d-flex justify-space-between align-center pa-6">
            <div class="d-flex align-center">
              <v-icon icon="mdi-calendar-outline" class="mr-2" />
              <span class="text-h6">Próximos Eventos</span>
            </div>
            <v-btn
              variant="text"
              size="small"
              append-icon="mdi-chevron-right"
            >
              Ver agenda
            </v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-6">
            <div class="text-center pa-8">
              <v-icon icon="mdi-calendar-check-outline" size="64" color="grey-lighten-1" class="mb-4" />
              <div class="text-h6 text-medium-emphasis mb-2">
                Nenhum evento agendado
              </div>
              <div class="text-body-2 text-medium-emphasis mb-4">
                Seus próximos eventos aparecerão aqui
              </div>
              <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-plus"
              >
                Adicionar Evento
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Column -->
      <v-col cols="12" md="4">
        <!-- Quick Actions -->
        <v-card rounded="lg" class="mb-6">
          <v-card-title class="pa-6">
            <div class="d-flex align-center">
              <v-icon icon="mdi-lightning-bolt-outline" class="mr-2" />
              <span class="text-h6">Ações Rápidas</span>
            </div>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-4">
            <v-list density="compact">
              <v-list-item
                v-for="action in quickActions"
                :key="action.title"
                :prepend-icon="action.icon"
                :title="action.title"
                rounded="lg"
                class="mb-2"
                @click="action.action"
              />
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Financial Summary -->
        <v-card rounded="lg" class="mb-6">
          <v-card-title class="pa-6">
            <div class="d-flex align-center">
              <v-icon icon="mdi-wallet-outline" class="mr-2" />
              <span class="text-h6">Resumo Financeiro</span>
            </div>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-6">
            <div class="mb-4">
              <div class="text-caption text-medium-emphasis mb-1">
                Mensalidade
              </div>
              <div class="d-flex justify-space-between align-center">
                <div class="text-h6 font-weight-bold">
                  R$ 60,00
                </div>
                <v-chip
                  color="success"
                  size="small"
                  variant="flat"
                >
                  Em dia
                </v-chip>
              </div>
            </div>
            <v-divider class="my-4" />
            <div class="mb-4">
              <div class="text-caption text-medium-emphasis mb-1">
                Próximo vencimento
              </div>
              <div class="text-body-1 font-weight-medium">
                05/11/2025
              </div>
            </div>
            <v-btn
              color="primary"
              variant="outlined"
              block
              prepend-icon="mdi-qrcode"
              @click="showPixDialog = true"
            >
              Gerar PIX
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- PIX Payment Dialog -->
        <PixPaymentDialog v-model="showPixDialog" />

        <!-- Voluntary Donation Dialog -->
        <VoluntaryDonationDialog v-model="showDonationDialog" @success="onDonationSuccess" />

        <!-- Notifications -->
        <v-card rounded="lg">
          <v-card-title class="pa-6">
            <div class="d-flex align-center">
              <v-icon icon="mdi-bell-outline" class="mr-2" />
              <span class="text-h6">Notificações</span>
            </div>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-0">
            <v-list density="compact">
              <v-list-item
                v-for="(notification, index) in notifications"
                :key="index"
                class="px-6 py-3"
              >
                <template v-slot:prepend>
                  <v-badge
                    v-if="!notification.read"
                    dot
                    color="primary"
                  >
                    <v-icon :icon="notification.icon" size="20" />
                  </v-badge>
                  <v-icon v-else :icon="notification.icon" size="20" />
                </template>
                <v-list-item-title class="text-body-2">
                  {{ notification.title }}
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">
                  {{ notification.time }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <div v-if="notifications.length === 0" class="pa-8 text-center">
              <v-icon icon="mdi-bell-off-outline" size="48" color="grey-lighten-1" class="mb-3" />
              <div class="text-body-2 text-medium-emphasis">
                Nenhuma notificação
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PixPaymentDialog from '@/components/finance/PixPaymentDialog.vue'
import VoluntaryDonationDialog from '@/components/donations/VoluntaryDonationDialog.vue'

const router = useRouter()
const authStore = useAuthStore()

// Dialog states
const showPixDialog = ref(false)
const showDonationDialog = ref(false)

// Real-time stats
const activeCasesCount = ref(0)
const completedCasesCount = ref(0)
const totalMembersCount = ref(0)
const totalDonations = ref('0,00')

// Load real statistics
async function loadStats() {
  try {
    // Load active cases count (exclude completed)
    const activeCasesResponse = await fetch('/api/assistance/cases/?exclude_status=completed', {
      headers: { 'Authorization': `Token ${authStore.token}` }
    })
    if (activeCasesResponse.ok) {
      const activeCasesData = await activeCasesResponse.json()
      activeCasesCount.value = activeCasesData.count
    }

    // Load completed cases count
    const completedCasesResponse = await fetch('/api/assistance/cases/?status=completed', {
      headers: { 'Authorization': `Token ${authStore.token}` }
    })
    if (completedCasesResponse.ok) {
      const completedCasesData = await completedCasesResponse.json()
      completedCasesCount.value = completedCasesData.count
    }

    // For admin/board, load additional stats
    if (authStore.user?.role !== 'MEMBER') {
      // Load members count (if endpoint exists)
      try {
        const membersResponse = await fetch('/api/users/profiles/', {
          headers: { 'Authorization': `Token ${authStore.token}` }
        })
        if (membersResponse.ok) {
          const membersData = await membersResponse.json()
          totalMembersCount.value = membersData.count || membersData.length
        }
      } catch (e) {
        console.log('Members count not available')
      }

      // Load donations total (if endpoint exists)
      try {
        const donationsResponse = await fetch('/api/finance/donations/', {
          headers: { 'Authorization': `Token ${authStore.token}` }
        })
        if (donationsResponse.ok) {
          const donationsData = await donationsResponse.json()
          const total = donationsData.results?.reduce((sum: number, d: any) => {
            return sum + (parseFloat(d.amount) || 0)
          }, 0) || 0
          totalDonations.value = total.toFixed(2).replace('.', ',')
        }
      } catch (e) {
        console.log('Donations not available')
      }
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

// Stats data with real values
const stats = computed(() => {
  const isMember = authStore.user?.role === 'MEMBER'

  if (isMember) {
    return [
      {
        title: 'Meus Casos Ativos',
        value: activeCasesCount.value.toString(),
        icon: 'mdi-progress-clock',
        color: 'primary',
        iconBg: 'rgba(255, 255, 255, 0.2)'
      },
      {
        title: 'Casos Concluídos',
        value: completedCasesCount.value.toString(),
        icon: 'mdi-check-circle',
        color: 'success',
        iconBg: 'rgba(255, 255, 255, 0.2)'
      },
      {
        title: 'Total de Casos',
        value: (activeCasesCount.value + completedCasesCount.value).toString(),
        icon: 'mdi-file-document',
        color: 'info',
        iconBg: 'rgba(255, 255, 255, 0.2)'
      },
      {
        title: 'Status',
        value: 'Ativo',
        icon: 'mdi-account-check',
        color: 'secondary',
        iconBg: 'rgba(255, 255, 255, 0.2)'
      }
    ]
  }

  // Admin/Board stats
  return [
    {
      title: 'Casos Ativos',
      value: activeCasesCount.value.toString(),
      icon: 'mdi-heart-pulse',
      color: 'primary',
      iconBg: 'rgba(255, 255, 255, 0.2)'
    },
    {
      title: 'Membros',
      value: totalMembersCount.value.toString(),
      icon: 'mdi-account-group',
      color: 'secondary',
      iconBg: 'rgba(255, 255, 255, 0.2)'
    },
    {
      title: 'Doações',
      value: `R$ ${totalDonations.value}`,
      icon: 'mdi-hand-heart',
      color: 'success',
      iconBg: 'rgba(255, 255, 255, 0.2)'
    },
    {
      title: 'Concluídos',
      value: completedCasesCount.value.toString(),
      icon: 'mdi-check-all',
      color: 'info',
      iconBg: 'rgba(255, 255, 255, 0.2)'
    }
  ]
})

// Recent activities
const recentActivities = ref([
  {
    title: 'Novo caso criado',
    description: 'Assistência médica para Maria Silva',
    time: 'Há 2 horas',
    icon: 'mdi-file-document-plus',
    color: 'primary'
  },
  {
    title: 'Doação recebida',
    description: 'João Santos doou R$ 200,00',
    time: 'Há 5 horas',
    icon: 'mdi-currency-usd',
    color: 'success'
  },
  {
    title: 'Caso aprovado',
    description: 'Assistência alimentar aprovada',
    time: 'Ontem',
    icon: 'mdi-check-circle',
    color: 'success'
  }
])

// Notifications
const notifications = ref([
  {
    title: 'Mensalidade vencendo em 5 dias',
    time: 'Agora',
    icon: 'mdi-alert-circle-outline',
    read: false
  },
  {
    title: 'Novo membro adicionado',
    time: 'Há 2 horas',
    icon: 'mdi-account-plus',
    read: false
  },
  {
    title: 'Relatório mensal disponível',
    time: 'Ontem',
    icon: 'mdi-file-chart',
    read: true
  }
])

// Quick actions
const quickActions = computed(() => {
  const actions = [
    {
      title: 'Fazer Doação',
      icon: 'mdi-hand-heart-outline',
      action: () => showDonationDialog.value = true
    },
    {
      title: 'Ver Casos',
      icon: 'mdi-heart-outline',
      action: () => router.push('/cases')
    },
    {
      title: 'Meu Perfil',
      icon: 'mdi-account-outline',
      action: () => router.push('/profile')
    }
  ]

  if (authStore.canCreateCases) {
    actions.unshift({
      title: 'Criar Novo Caso',
      icon: 'mdi-plus-circle-outline',
      action: () => router.push('/cases/new')
    })
  }

  return actions
})

// Methods
function getWelcomeMessage() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Bom dia! Aqui está o resumo de hoje.'
  if (hour < 18) return 'Boa tarde! Confira as novidades.'
  return 'Boa noite! Veja o que aconteceu hoje.'
}

function onDonationSuccess() {
  // Reload stats after successful donation
  loadStats()
  // Could also show a success message or open PIX dialog
  console.log('Donation registered successfully')
}

// Load stats on mount
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stat-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
}

.v-list-item {
  transition: background-color 0.2s ease;
}

.v-list-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.04);
}
</style>
