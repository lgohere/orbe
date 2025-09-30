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
            >
              Gerar PIX
            </v-btn>
          </v-card-text>
        </v-card>

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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Stats data
const stats = computed(() => [
  {
    title: 'Casos Ativos',
    value: '12',
    change: '+3 este mês',
    changePositive: true,
    icon: 'mdi-heart-pulse',
    color: 'primary',
    iconBg: 'rgba(255, 255, 255, 0.2)'
  },
  {
    title: 'Membros',
    value: '48',
    change: '+5 este mês',
    changePositive: true,
    icon: 'mdi-account-group',
    color: 'secondary',
    iconBg: 'rgba(255, 255, 255, 0.2)'
  },
  {
    title: 'Doações',
    value: 'R$ 3.2k',
    change: '+12% este mês',
    changePositive: true,
    icon: 'mdi-hand-heart',
    color: 'success',
    iconBg: 'rgba(255, 255, 255, 0.2)'
  },
  {
    title: 'Pendências',
    value: '3',
    change: '-2 esta semana',
    changePositive: true,
    icon: 'mdi-clock-alert-outline',
    color: 'warning',
    iconBg: 'rgba(255, 255, 255, 0.2)'
  }
])

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
      action: () => router.push('/donations/new')
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
