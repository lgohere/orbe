<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar
      :elevation="0"
      :color="theme.current.value.dark ? 'surface' : 'white'"
      class="app-bar"
    >
      <!-- Mobile Menu Toggle -->
      <v-app-bar-nav-icon
        v-if="mobile"
        @click="drawer = !drawer"
        class="ml-2"
      />

      <!-- Logo -->
      <div class="d-flex align-center ml-4">
        <v-img
          src="/orbe-logo.png"
          alt="ORBE"
          max-width="40"
          height="40"
          class="mr-3"
        />
        <div class="logo-text">
          <div class="text-h6 font-weight-bold primary--text">ORBE</div>
          <div class="text-caption text-medium-emphasis">Real Bem-Estar</div>
        </div>
      </div>

      <v-spacer />

      <!-- Search Bar (Desktop) -->
      <v-text-field
        v-if="!mobile"
        prepend-inner-icon="mdi-magnify"
        placeholder="Buscar..."
        variant="outlined"
        density="compact"
        hide-details
        single-line
        class="search-field mx-4"
        style="max-width: 400px"
      />

      <!-- Theme Toggle -->
      <v-btn
        :icon="theme.current.value.dark ? 'mdi-white-balance-sunny' : 'mdi-weather-night'"
        variant="text"
        @click="toggleTheme"
      />

      <!-- Notifications -->
      <v-btn icon variant="text" class="mx-2">
        <v-badge color="error" content="3" dot>
          <v-icon>mdi-bell-outline</v-icon>
        </v-badge>
      </v-btn>

      <!-- User Menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            variant="text"
            class="mr-2"
          >
            <v-avatar size="36" color="primary">
              <span class="text-white text-body-2">
                {{ userInitials }}
              </span>
            </v-avatar>
          </v-btn>
        </template>
        <v-list min-width="200">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              {{ authStore.fullName }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ getRoleLabel(authStore.user?.role) }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item @click="$router.push('/profile')" prepend-icon="mdi-account-outline">
            <v-list-item-title>Meu Perfil</v-list-item-title>
          </v-list-item>
          <v-list-item @click="$router.push('/settings')" prepend-icon="mdi-cog-outline">
            <v-list-item-title>Configurações</v-list-item-title>
          </v-list-item>
          <v-divider />
          <v-list-item @click="handleLogout" prepend-icon="mdi-logout">
            <v-list-item-title>Sair</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      :permanent="!mobile"
      :temporary="mobile"
      width="260"
      :color="theme.current.value.dark ? 'surface' : 'white'"
      class="navigation-drawer"
    >
      <!-- User Info Card -->
      <v-card
        flat
        class="ma-4 pa-4"
        :color="theme.current.value.dark ? 'primary' : 'primary'"
        dark
      >
        <div class="d-flex align-center">
          <v-avatar size="48" color="white">
            <span class="text-primary text-h6 font-weight-bold">
              {{ userInitials }}
            </span>
          </v-avatar>
          <div class="ml-3">
            <div class="text-body-1 font-weight-bold">
              {{ authStore.user?.first_name }}
            </div>
            <div class="text-caption">
              {{ getRoleLabel(authStore.user?.role) }}
            </div>
          </div>
        </div>
      </v-card>

      <!-- Navigation Menu -->
      <v-list density="compact" nav class="px-2">
        <v-list-item
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="lg"
          class="mb-1"
        />
      </v-list>

      <template v-slot:append>
        <!-- Quick Actions - Removed "Novo Caso" button -->
      </template>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main class="main-content">
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme, useDisplay } from 'vuetify'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const theme = useTheme()
const { mobile } = useDisplay()
const authStore = useAuthStore()

// Drawer state
const drawer = ref(true)

// Computed
const userInitials = computed(() => {
  if (!authStore.user) return '?'
  const first = authStore.user.first_name?.charAt(0) || ''
  const last = authStore.user.last_name?.charAt(0) || ''
  return `${first}${last}`.toUpperCase()
})

// Menu items based on role
const menuItems = computed(() => {
  const items = [
    { path: '/dashboard', icon: 'mdi-view-dashboard-outline', title: 'Dashboard' },
    { path: '/finance', icon: 'mdi-wallet-outline', title: 'Finanças' },
    { path: '/cases', icon: 'mdi-heart-outline', title: 'Atendimentos' },
    { path: '/feed', icon: 'mdi-bulletin-board', title: 'Feed' },
    { path: '/members', icon: 'mdi-account-group-outline', title: 'Membros' },
  ]

  // Add admin-only items
  if (authStore.isAdmin || authStore.isBoardMember) {
    items.push(
      { path: '/reports', icon: 'mdi-chart-line', title: 'Relatórios' },
      { path: '/settings', icon: 'mdi-cog-outline', title: 'Configurações' }
    )
  }

  return items
})

// Methods
function toggleTheme() {
  const newTheme = theme.current.value.dark ? 'orbe-white' : 'orbe-black'
  theme.change(newTheme)

  // Save preference to backend
  authStore.updatePreferences({
    theme_preference: theme.current.value.dark ? 'black' : 'white'
  })
}

function getRoleLabel(role?: string) {
  const labels: Record<string, string> = {
    'SUPER_ADMIN': 'Administrador',
    'BOARD': 'Conselho Diretor',
    'FISCAL_COUNCIL': 'Conselho Fiscal',
    'MEMBER': 'Membro'
  }
  return labels[role || ''] || 'Membro'
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.logo-text {
  line-height: 1.2;
}

.navigation-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.05);
}

.search-field :deep(.v-field) {
  border-radius: 12px;
}

.main-content {
  background: rgb(var(--v-theme-background));
}

/* Smooth transitions */
.v-list-item {
  transition: all 0.2s ease;
}

.v-list-item:hover {
  transform: translateX(4px);
}
</style>
