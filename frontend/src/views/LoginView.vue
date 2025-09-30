<template>
  <div class="login-container">
    <!-- Language Toggle (Top Right) -->
    <div class="language-toggle">
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            variant="outlined"
            color="primary"
            size="small"
            prepend-icon="mdi-web"
            class="rounded-pill elevation-2"
          >
            {{ currentLanguageLabel }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item
            v-for="lang in languageOptions"
            :key="lang.value"
            @click="changeLanguage(lang.value)"
            :class="{ 'v-list-item--active': currentLanguage === lang.value }"
          >
            <v-list-item-title>{{ lang.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>

    <v-container class="fill-height" fluid>
      <v-row justify="center" align="center" class="fill-height">
        <v-col cols="12" sm="10" md="6" lg="5" xl="4">
          <!-- ORBE Logo and Branding -->
          <div class="text-center mb-8">
            <div class="orbe-logo mb-4">
              <v-icon size="64" color="primary">mdi-account-group</v-icon>
            </div>
            <h1 class="orbe-title text-h3 text-primary mb-2" style="letter-spacing: 2px;">
              {{ $t('organization.name') }}
            </h1>
            <p class="orbe-subtitle text-h6 text-medium-emphasis">
              {{ $t('organization.fullName') }}
            </p>
          </div>

          <!-- Main Card -->
          <v-card class="elevation-8 rounded-xl overflow-hidden">
            <!-- Header -->
            <div class="login-header pa-8 pb-4">
              <div class="text-center mb-4">
                <v-avatar size="48" color="primary" class="mb-4">
                  <v-icon size="24" color="white">mdi-login</v-icon>
                </v-avatar>
                <h2 class="orbe-title text-h4 text-primary mb-2">
                  Acesso ORBE
                </h2>
                <p class="orbe-body text-body-2 text-medium-emphasis">
                  Acesse sua conta na plataforma ORBE
                </p>
              </div>
            </div>

            <!-- Form -->
            <v-card-text class="pa-8 pt-4">
              <v-form @submit.prevent="handleLogin" ref="form">
                <v-row>
                  <!-- Email -->
                  <v-col cols="12">
                    <v-text-field
                      v-model="formData.email"
                      :label="$t('common.email')"
                      placeholder="seu@email.com"
                      variant="outlined"
                      type="email"
                      required
                      prepend-inner-icon="mdi-email"
                      density="comfortable"
                      color="primary"
                      :rules="[rules.required, rules.email]"
                      class="rounded-lg"
                    />
                  </v-col>

                  <!-- Password -->
                  <v-col cols="12">
                    <v-text-field
                      v-model="formData.password"
                      :label="$t('common.password')"
                      placeholder="Sua senha"
                      variant="outlined"
                      :type="showPassword ? 'text' : 'password'"
                      required
                      prepend-inner-icon="mdi-lock"
                      :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      @click:append-inner="showPassword = !showPassword"
                      density="comfortable"
                      color="primary"
                      :rules="[rules.required]"
                      class="rounded-lg"
                    />
                  </v-col>

                  <!-- Remember Me & Forgot Password -->
                  <v-col cols="12" class="d-flex justify-space-between align-center">
                    <v-checkbox
                      v-model="formData.rememberMe"
                      label="Lembrar-me"
                      color="primary"
                      density="compact"
                      class="ma-0"
                    />
                    <v-btn
                      variant="text"
                      color="primary"
                      size="small"
                      @click="goToForgotPassword"
                    >
                      {{ $t('auth.forgotPassword') }}
                    </v-btn>
                  </v-col>

                  <!-- Error Alert -->
                  <v-col cols="12" v-if="errorMessage">
                    <v-alert
                      type="error"
                      variant="tonal"
                      density="compact"
                      :text="errorMessage"
                    />
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>

            <!-- Actions -->
            <v-card-actions class="pa-8 pt-4">
              <v-row no-gutters>
                <!-- Login Button -->
                <v-col cols="12" class="mb-4">
                  <v-btn
                    type="submit"
                    @click="handleLogin"
                    color="primary"
                    size="x-large"
                    block
                    :loading="isLoading"
                    :disabled="!isFormValid || isLoading"
                    class="rounded-pill font-weight-bold"
                  >
                    {{ isLoading ? $t('common.loading') : $t('auth.login') }}
                  </v-btn>
                </v-col>

                <!-- Divider -->
                <v-col cols="12" class="mb-4">
                  <div class="d-flex align-center">
                    <v-divider />
                    <span class="px-4 text-body-2 text-medium-emphasis">ou</span>
                    <v-divider />
                  </div>
                </v-col>

                <!-- Google Login -->
                <v-col cols="12" class="mb-4">
                  <v-btn
                    @click="handleGoogleLogin"
                    variant="outlined"
                    color="primary"
                    size="large"
                    block
                    prepend-icon="mdi-google"
                    class="rounded-pill"
                  >
                    {{ $t('auth.loginWithGoogle') }}
                  </v-btn>
                </v-col>

                <!-- Register Link -->
                <v-col cols="12" class="text-center">
                  <p class="text-body-2 text-medium-emphasis mb-2">
                    {{ $t('auth.dontHaveAccount') }}
                  </p>
                  <v-btn
                    @click="goToRegister"
                    variant="text"
                    color="secondary"
                    class="font-weight-bold"
                  >
                    {{ $t('auth.register') }}
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const { locale, t } = useI18n()
const authStore = useAuthStore()

// State
const form = ref()
const showPassword = ref(false)

// Language options
const languageOptions = [
  { value: 'pt-br', label: '🇧🇷 Português' },
  { value: 'en', label: '🇺🇸 English' },
  { value: 'es', label: '🇪🇸 Español' }
]

// Current language computed
const currentLanguage = computed(() => locale.value)
const currentLanguageLabel = computed(() => {
  const current = languageOptions.find(lang => lang.value === locale.value)
  return current?.label || '🇧🇷 Português'
})

// Form data
const formData = reactive({
  email: '',
  password: '',
  rememberMe: false
})

// Validation rules
const rules = {
  required: (value: string) => !!value || t('common.required'),
  email: (value: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || t('validation.email')
  }
}

// Computed
const isFormValid = computed(() => {
  return formData.email?.length > 0 &&
         formData.password?.length > 0 &&
         rules.email(formData.email) === true
})

const isLoading = computed(() => authStore.isLoading)
const errorMessage = computed(() => authStore.error || '')

// Methods
function changeLanguage(newLanguage: string) {
  locale.value = newLanguage
  localStorage.setItem('orbe-language', newLanguage)
}

async function handleLogin() {
  if (!isFormValid.value) return

  const { valid } = await form.value.validate()
  if (!valid) return

  const success = await authStore.login({
    email: formData.email,
    password: formData.password
  })

  if (success) {
    // LOGIN: Always redirect to dashboard (not onboarding)
    // Onboarding is only for NEW registrations, not returning users
    router.push('/dashboard')
  }
}

function handleGoogleLogin() {
  // Redirect to Google OAuth endpoint
  window.location.href = '/accounts/google/login/'
}

function goToForgotPassword() {
  router.push('/auth/forgot-password')
}

function goToRegister() {
  router.push('/onboarding')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #DDEAF4 0%, #FFFFFF 100%);
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(48,78,105,0.05)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  pointer-events: none;
}

.language-toggle {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 10;
}

.orbe-logo {
  position: relative;
  z-index: 1;
}

.login-header {
  background: linear-gradient(135deg, rgba(199, 150, 87, 0.05) 0%, rgba(48, 78, 105, 0.05) 100%);
  border-bottom: 1px solid rgba(48, 78, 105, 0.1);
}

.rounded-lg :deep(.v-field) {
  border-radius: 12px;
}

.rounded-pill {
  border-radius: 28px;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .login-container {
    padding: 1rem;
  }

  .orbe-logo .v-icon {
    font-size: 48px !important;
  }

  .text-h3 {
    font-size: 1.8rem !important;
  }

  .text-h6 {
    font-size: 1.1rem !important;
  }

  .text-h4 {
    font-size: 1.5rem !important;
  }

  .pa-8 {
    padding: 1.5rem !important;
  }

  .login-header {
    padding: 1.5rem 1.5rem 1rem !important;
  }
}
</style>