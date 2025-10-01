import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/login'
    },
    // Public routes (no layout)
    {
      path: '/onboarding',
      name: 'onboarding',
      component: () => import('../views/OnboardingView.vue'),
      meta: {
        requiresAuth: false,
        title: 'Bem-vindo à ORBE'
      }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: {
        requiresAuth: false,
        title: 'Login'
      }
    },
    {
      path: '/set-password',
      name: 'set-password',
      component: () => import('../views/SetPasswordView.vue'),
      meta: {
        requiresAuth: false,
        title: 'Configurar Senha'
      }
    },
    // Authenticated routes (with AppLayout)
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Dashboard'
          }
        },
        {
          path: 'finance',
          name: 'finance',
          component: () => import('../views/DashboardView.vue'), // Placeholder - will create later
          meta: {
            requiresAuth: true,
            title: 'Finanças'
          }
        },
        {
          path: 'cases',
          name: 'cases',
          component: () => import('../views/cases/CasesListView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Casos de Assistência'
          }
        },
        {
          path: 'cases/create',
          name: 'case-create',
          component: () => import('../views/cases/CaseFormView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Novo Caso',
            requiresBoard: true
          }
        },
        {
          path: 'cases/:id',
          name: 'case-detail',
          component: () => import('../views/cases/CaseDetailView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Detalhes do Caso'
          }
        },
        {
          path: 'cases/:id/edit',
          name: 'case-edit',
          component: () => import('../views/cases/CaseFormView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Editar Caso',
            requiresBoard: true
          }
        },
        {
          path: 'feed',
          name: 'feed',
          component: () => import('../views/DashboardView.vue'), // Placeholder - will create later
          meta: {
            requiresAuth: true,
            title: 'Feed'
          }
        },
        {
          path: 'members',
          name: 'members',
          component: () => import('../views/DashboardView.vue'), // Placeholder - will create later
          meta: {
            requiresAuth: true,
            title: 'Membros'
          }
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/DashboardView.vue'), // Placeholder - will create later
          meta: {
            requiresAuth: true,
            title: 'Relatórios'
          }
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('../views/DashboardView.vue'), // Placeholder - will create later
          meta: {
            requiresAuth: true,
            title: 'Configurações'
          }
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/ProfileView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Meu Perfil'
          }
        }
      ]
    },
    // 404 route
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
      meta: {
        title: 'Página não encontrada'
      }
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} | ORBE Platform` : 'ORBE Platform'

  const authStore = useAuthStore()

  // Initialize auth store on first load
  if (!authStore.user && authStore.token) {
    await authStore.initialize()
  }

  // Check authentication requirement
  const requiresAuth = to.meta.requiresAuth as boolean
  const isAuthenticated = authStore.isAuthenticated

  if (requiresAuth && !isAuthenticated) {
    // Redirect to login if authentication is required but user is not authenticated
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  if (!requiresAuth && isAuthenticated && (to.name === 'login' || to.name === 'home')) {
    // Redirect authenticated users away from login page
    next({ name: 'dashboard' })
    return
  }

  // Check role-based permissions
  const requiresBoard = to.meta.requiresBoard as boolean
  if (requiresBoard && !authStore.canCreateCases) {
    // Redirect non-Board users away from Board-only pages
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router