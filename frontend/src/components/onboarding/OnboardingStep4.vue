<template>
  <div class="step-container">
    <!-- Header -->
    <div class="step-header pa-8 pb-4">
      <div class="text-center mb-4">
        <v-avatar size="48" color="secondary" class="mb-4">
          <v-icon size="24" color="white">mdi-shield-check</v-icon>
        </v-avatar>
        <h3 class="orbe-title text-h5 text-primary mb-2">
          {{ $t('onboarding.step4.title') }}
        </h3>
        <p class="orbe-body text-body-2 text-medium-emphasis">
          {{ $t('onboarding.step4.subtitle') }}
        </p>
      </div>
    </div>

    <!-- Form -->
    <v-card-text class="pa-8 pt-4">
      <v-form @submit.prevent="handleFinish" ref="form">
        <v-row>
          <v-col cols="12">
            <!-- Terms and Conditions -->
            <v-card variant="outlined" class="pa-4 mb-4">
              <div class="d-flex align-start">
                <v-checkbox
                  v-model="modelValue.terms_accepted"
                  color="primary"
                  density="compact"
                  class="me-3 mt-n1"
                />
                <div>
                  <p class="orbe-body text-body-2 mb-0">
                    {{ $t('onboarding.step4.termsText') }}
                    <v-btn
                      variant="text"
                      color="primary"
                      size="small"
                      class="pa-0 text-decoration-underline"
                      @click="showTerms = true"
                    >
                      {{ $t('onboarding.step4.termsLink') }}
                    </v-btn>
                    da ORBE
                  </p>
                </div>
              </div>
            </v-card>

            <!-- Privacy Policy -->
            <v-card variant="outlined" class="pa-4 mb-4">
              <div class="d-flex align-start">
                <v-checkbox
                  v-model="modelValue.privacy_accepted"
                  color="primary"
                  density="compact"
                  class="me-3 mt-n1"
                />
                <div>
                  <p class="orbe-body text-body-2 mb-0">
                    {{ $t('onboarding.step4.privacyText') }}
                    <v-btn
                      variant="text"
                      color="primary"
                      size="small"
                      class="pa-0 text-decoration-underline"
                      @click="showPrivacy = true"
                    >
                      {{ $t('onboarding.step4.privacyLink') }}
                    </v-btn>
                    da ORBE
                  </p>
                </div>
              </div>
            </v-card>

            <!-- Data Confirmation -->
            <v-card variant="outlined" class="pa-4">
              <div class="d-flex align-start">
                <v-checkbox
                  v-model="confirmInfo"
                  color="primary"
                  density="compact"
                  class="me-3 mt-n1"
                />
                <div>
                  <p class="orbe-body text-body-2 mb-0">
                    {{ $t('onboarding.step4.confirmText') }}
                  </p>
                </div>
              </div>
            </v-card>

            <!-- Error Alert -->
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mt-4"
              density="compact"
            >
              {{ error }}
            </v-alert>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>

    <!-- Actions -->
    <v-card-actions class="pa-8 pt-4">
      <v-row no-gutters>
        <v-col cols="5">
          <v-btn
            @click="$emit('previous')"
            variant="outlined"
            color="primary"
            size="large"
            block
            prepend-icon="mdi-arrow-left"
            class="rounded-pill"
            :disabled="loading"
          >
            {{ $t('common.previous') }}
          </v-btn>
        </v-col>
        <v-col cols="2" class="d-flex align-center justify-center">
          <v-divider vertical class="mx-2" />
        </v-col>
        <v-col cols="5">
          <v-btn
            type="submit"
            @click="handleFinish"
            color="secondary"
            size="large"
            block
            append-icon="mdi-check"
            class="rounded-pill font-weight-bold"
            :disabled="loading || !canFinish"
            :loading="loading"
          >
            {{ loading ? $t('common.loading') : $t('common.finish') }}
          </v-btn>
        </v-col>
      </v-row>
    </v-card-actions>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface FormData {
  terms_accepted: boolean
  privacy_accepted: boolean
  // ... other fields
}

const props = defineProps<{
  modelValue: FormData
  loading?: boolean
}>()

const emit = defineEmits<{
  finish: []
  previous: []
}>()

const form = ref()
const { t } = useI18n()

// Local state
const confirmInfo = ref(false)
const error = ref('')
const showTerms = ref(false)
const showPrivacy = ref(false)

// Computed
const canFinish = computed(() => {
  return props.modelValue.terms_accepted &&
         props.modelValue.privacy_accepted &&
         confirmInfo.value
})

function handleFinish() {
  error.value = ''

  if (!canFinish.value) {
    error.value = t('validation.acceptTerms')
    return
  }

  emit('finish')
}
</script>

<style scoped>
.step-container {
  min-height: 400px;
}

.step-header {
  background: linear-gradient(135deg, rgba(199, 150, 87, 0.05) 0%, rgba(48, 78, 105, 0.05) 100%);
  border-bottom: 1px solid rgba(48, 78, 105, 0.1);
}

.rounded-pill {
  border-radius: 28px;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .pa-8 {
    padding: 1.5rem !important;
  }

  .step-header {
    padding: 1.5rem 1.5rem 1rem !important;
  }
}
</style>