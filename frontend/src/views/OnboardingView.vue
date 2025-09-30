<template>
  <div class="onboarding-container">
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
        <v-col cols="12" sm="10" md="8" lg="6" xl="5">
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
            <!-- Progress Bar -->
            <div class="progress-header">
              <v-progress-linear
                :model-value="(currentStep / 4) * 100"
                color="secondary"
                height="4"
                rounded
              />
            </div>

            <!-- Content -->
            <v-card-text class="pa-0">
              <v-window v-model="currentStep" class="onboarding-window">
                <!-- Welcome Step -->
                <v-window-item :value="0" class="pa-8 text-center">
                  <div class="welcome-content">
                    <v-icon size="72" color="secondary" class="mb-6">mdi-hand-wave</v-icon>
                    <h2 class="orbe-title text-h4 text-primary mb-4">
                      {{ $t('onboarding.welcome') }}
                    </h2>
                    <p class="orbe-body text-body-1 text-medium-emphasis mb-8 px-4">
                      {{ $t('onboarding.subtitle') }}
                    </p>
                    <v-btn
                      @click="nextStep"
                      color="secondary"
                      size="x-large"
                      rounded="pill"
                      min-width="200"
                      elevation="2"
                      class="text-h6 font-weight-bold"
                    >
                      Começar
                      <v-icon end>mdi-arrow-right</v-icon>
                    </v-btn>
                  </div>
                </v-window-item>

                <!-- Step 1: Personal Information -->
                <v-window-item :value="1">
                  <OnboardingStep1
                    v-model="formData"
                    @next="nextStep"
                    @previous="previousStep"
                  />
                </v-window-item>

                <!-- Step 2: Address -->
                <v-window-item :value="2">
                  <OnboardingStep2
                    v-model="formData"
                    @next="nextStep"
                    @previous="previousStep"
                  />
                </v-window-item>

                <!-- Step 3: Preferences -->
                <v-window-item :value="3">
                  <OnboardingStep3
                    v-model="formData"
                    @next="nextStep"
                    @previous="previousStep"
                  />
                </v-window-item>

                <!-- Step 4: Terms -->
                <v-window-item :value="4">
                  <OnboardingStep4
                    v-model="formData"
                    @finish="finishOnboarding"
                    @previous="previousStep"
                    :loading="isSubmitting"
                  />
                </v-window-item>

                <!-- Completion -->
                <v-window-item :value="5">
                  <OnboardingComplete />
                </v-window-item>
              </v-window>
            </v-card-text>
          </v-card>

          <!-- Step Indicator -->
          <div v-if="currentStep > 0 && currentStep <= 4" class="text-center mt-4">
            <p class="orbe-caption text-medium-emphasis">
              Passo {{ currentStep }} de 4
            </p>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import OnboardingStep1 from '../components/onboarding/OnboardingStep1.vue'
import OnboardingStep2 from '../components/onboarding/OnboardingStep2.vue'
import OnboardingStep3 from '../components/onboarding/OnboardingStep3.vue'
import OnboardingStep4 from '../components/onboarding/OnboardingStep4.vue'
import OnboardingComplete from '../components/onboarding/OnboardingComplete.vue'
import { apiService, type OnboardingData } from '../services/api'

const router = useRouter()
const { locale } = useI18n()

// State
const currentStep = ref(0)
const isSubmitting = ref(false)

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
  // Step 1: Personal info
  first_name: '',
  last_name: '',
  email: '',
  phone: '',

  // Step 2: Address
  city: '',
  state: '',
  country: 'Brasil',

  // Step 3: Preferences
  membership_due_day: 5,
  theme_preference: 'white',
  language_preference: 'pt-br',

  // Step 4: Terms
  terms_accepted: false,
  privacy_accepted: false
})

// Methods
function changeLanguage(newLanguage: string) {
  locale.value = newLanguage
  localStorage.setItem('orbe-language', newLanguage)
  formData.language_preference = newLanguage
}

function nextStep() {
  if (currentStep.value < 5) {
    currentStep.value++
  }
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function finishOnboarding() {
  if (isSubmitting.value) return

  try {
    isSubmitting.value = true

    // ARCHITECTURE NOTE:
    // Onboarding is only accessible by NEW users who just registered.
    // The user must already be authenticated (have a token from registration).
    // This endpoint only UPDATES the user's profile data, it does NOT create the user.

    // Prepare data for API submission
    const onboardingData: OnboardingData = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      email: formData.email,
      phone: formData.phone,
      city: formData.city,
      state: formData.state,
      country: formData.country,
      membership_due_day: formData.membership_due_day,
      theme_preference: formData.theme_preference,
      language_preference: formData.language_preference,
      terms_accepted: formData.terms_accepted,
      privacy_accepted: formData.privacy_accepted
    }

    console.log('Submitting onboarding data:', onboardingData)

    // Submit to backend API (updates profile for authenticated user)
    const response = await apiService.submitOnboarding(onboardingData)

    if (response.error) {
      console.error('Onboarding submission failed:', response.error)
      alert(`Erro ao atualizar perfil: ${response.error}`)
      return
    }

    console.log('Onboarding successful:', response.data)

    // Go to completion step
    currentStep.value = 5

    // Redirect to dashboard after 2 seconds
    setTimeout(() => {
      router.push('/dashboard')
    }, 2000)

  } catch (error) {
    console.error('Onboarding submission failed:', error)
    alert('Erro de conexão. Tente novamente.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.onboarding-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #DDEAF4 0%, #FFFFFF 100%);
  position: relative;
}

.onboarding-container::before {
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

.progress-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 1rem 1.5rem 0;
}

.onboarding-window {
  min-height: 400px;
}

.welcome-content {
  max-width: 400px;
  margin: 0 auto;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .onboarding-container {
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

  .welcome-content .v-icon {
    font-size: 56px !important;
  }

  .text-h4 {
    font-size: 1.5rem !important;
  }
}
</style>