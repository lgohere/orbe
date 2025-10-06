<template>
  <v-container fluid class="fill-height pa-0">
    <v-row no-gutters class="fill-height">
      <!-- Left side - Branding -->
      <v-col cols="12" md="6" class="d-none d-md-flex align-center justify-center primary">
        <div class="text-center px-8">
          <v-img
            src="@/assets/orbe-logo.png"
            alt="ORBE Logo"
            max-width="280"
            class="mx-auto mb-8"
          />
          <h1 class="text-h3 font-weight-bold white--text mb-4">
            Bem-vindo à ORBE
          </h1>
          <p class="text-h6 white--text text--lighten-1">
            Configure sua senha e comece sua jornada conosco
          </p>
        </div>
      </v-col>

      <!-- Right side - Password Setup Form -->
      <v-col cols="12" md="6" class="d-flex align-center justify-center">
        <v-card flat max-width="500" width="100%" class="pa-8">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-12">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
              class="mb-4"
            />
            <p class="text-body-1 text-medium-emphasis">
              Validando convite...
            </p>
          </div>

          <!-- Invalid Token State -->
          <div v-else-if="tokenError" class="text-center py-8">
            <v-icon size="80" color="error" class="mb-4">
              mdi-alert-circle-outline
            </v-icon>
            <h2 class="text-h5 mb-4">Convite Inválido</h2>
            <p class="text-body-1 text-medium-emphasis mb-6">
              {{ tokenError }}
            </p>
            <v-btn color="primary" variant="flat" to="/login" block>
              Voltar ao Login
            </v-btn>
          </div>

          <!-- Password Setup Form -->
          <div v-else-if="invitation">
            <div class="text-center mb-8">
              <v-avatar color="primary" size="80" class="mb-4">
                <span class="text-h3 white--text">
                  {{ invitation.first_name.charAt(0) }}{{ invitation.last_name.charAt(0) }}
                </span>
              </v-avatar>
              <h1 class="text-h4 mb-2">
                Olá, {{ invitation.first_name }}!
              </h1>
              <p class="text-body-1 text-medium-emphasis">
                {{ invitation.email }}
              </p>
            </div>

            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mb-6"
              closable
              @click:close="error = ''"
            >
              {{ error }}
            </v-alert>

            <v-form ref="formRef" @submit.prevent="handleSubmit">
              <v-text-field
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                label="Senha"
                placeholder="Digite sua senha"
                :rules="passwordRules"
                variant="outlined"
                prepend-inner-icon="mdi-lock-outline"
                class="mb-4"
                @click:append-inner="showPassword = !showPassword"
                required
              />

              <v-text-field
                v-model="form.password_confirm"
                :type="showPasswordConfirm ? 'text' : 'password'"
                :append-inner-icon="showPasswordConfirm ? 'mdi-eye-off' : 'mdi-eye'"
                label="Confirmar Senha"
                placeholder="Digite sua senha novamente"
                :rules="passwordConfirmRules"
                variant="outlined"
                prepend-inner-icon="mdi-lock-check-outline"
                class="mb-2"
                @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
                required
              />

              <!-- Password Strength Indicator -->
              <div v-if="form.password" class="mb-6">
                <div class="d-flex align-center mb-2">
                  <span class="text-caption text-medium-emphasis">
                    Força da senha:
                  </span>
                  <v-spacer />
                  <span
                    class="text-caption font-weight-bold"
                    :class="passwordStrength.color + '--text'"
                  >
                    {{ passwordStrength.label }}
                  </span>
                </div>
                <v-progress-linear
                  :model-value="passwordStrength.value"
                  :color="passwordStrength.color"
                  height="6"
                  rounded
                />
              </div>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                variant="flat"
                block
                :loading="submitting"
                :disabled="!form.password || !form.password_confirm"
              >
                Criar Conta
              </v-btn>

              <div class="text-center mt-6">
                <p class="text-caption text-medium-emphasis">
                  Ao criar sua conta, você concorda com nossos
                  <a href="#" class="text-primary">Termos de Serviço</a> e
                  <a href="#" class="text-primary">Política de Privacidade</a>
                </p>
              </div>
            </v-form>

            <!-- Token Expiry Warning -->
            <v-alert
              v-if="expiresIn && expiresIn < 24"
              type="warning"
              variant="tonal"
              density="compact"
              class="mt-6"
            >
              <template v-slot:prepend>
                <v-icon>mdi-clock-alert-outline</v-icon>
              </template>
              Este convite expira em {{ expiresIn }} horas
            </v-alert>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiService } from '@/services/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Form refs
const formRef = ref<any>(null)

// Form state
const form = ref({
  password: '',
  password_confirm: ''
})

const showPassword = ref(false)
const showPasswordConfirm = ref(false)

// Component state
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const tokenError = ref('')
const invitation = ref<{
  email: string
  first_name: string
  last_name: string
  expires_at: string
} | null>(null)

// Validation rules
const passwordRules = [
  (v: string) => !!v || 'Senha é obrigatória',
  (v: string) => v.length >= 8 || 'Senha deve ter no mínimo 8 caracteres',
  (v: string) => /[A-Z]/.test(v) || 'Senha deve conter pelo menos uma letra maiúscula',
  (v: string) => /[a-z]/.test(v) || 'Senha deve conter pelo menos uma letra minúscula',
  (v: string) => /[0-9]/.test(v) || 'Senha deve conter pelo menos um número'
]

const passwordConfirmRules = [
  (v: string) => !!v || 'Confirmação de senha é obrigatória',
  (v: string) => v === form.value.password || 'As senhas não coincidem'
]

// Password strength calculation
const passwordStrength = computed(() => {
  const pwd = form.value.password
  if (!pwd) return { value: 0, label: '', color: 'grey' }

  let strength = 0

  // Length check
  if (pwd.length >= 8) strength += 20
  if (pwd.length >= 12) strength += 20

  // Character variety
  if (/[a-z]/.test(pwd)) strength += 15
  if (/[A-Z]/.test(pwd)) strength += 15
  if (/[0-9]/.test(pwd)) strength += 15
  if (/[^a-zA-Z0-9]/.test(pwd)) strength += 15

  if (strength <= 30) {
    return { value: strength, label: 'Fraca', color: 'error' }
  } else if (strength <= 60) {
    return { value: strength, label: 'Média', color: 'warning' }
  } else if (strength <= 80) {
    return { value: strength, label: 'Boa', color: 'info' }
  } else {
    return { value: strength, label: 'Forte', color: 'success' }
  }
})

// Calculate hours until expiry
const expiresIn = computed(() => {
  if (!invitation.value) return null

  const expiryDate = new Date(invitation.value.expires_at)
  const now = new Date()
  const hoursLeft = Math.floor((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60))

  return hoursLeft > 0 ? hoursLeft : 0
})

// Validate token on mount
onMounted(async () => {
  const token = route.query.token as string

  if (!token) {
    tokenError.value = 'Token de convite não encontrado na URL.'
    loading.value = false
    return
  }

  try {
    const { data, error: apiError } = await apiService.validateInvitationToken(token)

    if (data && (data as any).valid) {
      invitation.value = (data as any).invitation
    } else {
      tokenError.value = apiError || (data as any)?.errors?.token?.[0] || 'Token de convite inválido ou expirado.'
    }
  } catch (err) {
    console.error('Error validating token:', err)
    tokenError.value = 'Erro ao validar o convite. Tente novamente mais tarde.'
  } finally {
    loading.value = false
  }
})

// Handle form submission
async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  submitting.value = true
  error.value = ''

  try {
    const token = route.query.token as string

    const response = await authStore.setupPassword({
      token,
      password: form.value.password,
      password_confirm: form.value.password_confirm
    })

    if (response.success) {
      // Password setup successful, redirect to dashboard (invited users already have profile data)
      router.push('/dashboard')
    } else {
      error.value = response.error || 'Erro ao criar conta. Tente novamente.'
    }
  } catch (err: any) {
    console.error('Error setting up password:', err)
    error.value = err.message || 'Erro ao criar conta. Tente novamente.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>
