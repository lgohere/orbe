<template>
  <div class="step-container">
    <!-- Header -->
    <div class="step-header pa-8 pb-4">
      <div class="text-center mb-4">
        <v-avatar size="48" color="secondary" class="mb-4">
          <v-icon size="24" color="white">mdi-cog</v-icon>
        </v-avatar>
        <h3 class="orbe-title text-h5 text-primary mb-2">
          {{ $t('onboarding.step3.title') }}
        </h3>
        <p class="orbe-body text-body-2 text-medium-emphasis">
          {{ $t('onboarding.step3.subtitle') }}
        </p>
      </div>
    </div>

    <!-- Form -->
    <v-card-text class="pa-8 pt-4">
      <v-form @submit.prevent="handleNext" ref="form">
        <v-row>
          <!-- Membership Due Day -->
          <v-col cols="12">
            <v-select
              v-model="modelValue.membership_due_day"
              :items="dayOptions"
              item-title="label"
              item-value="value"
              :label="$t('onboarding.step3.membershipDay')"
              :hint="$t('onboarding.step3.membershipDayHelper')"
              persistent-hint
              variant="outlined"
              prepend-inner-icon="mdi-calendar"
              density="comfortable"
              color="primary"
              class="rounded-lg"
            />
          </v-col>

          <!-- Theme Selection -->
          <v-col cols="12">
            <p class="orbe-body text-body-2 mb-4 font-weight-medium">
              <v-icon start size="small">mdi-palette</v-icon>
              {{ $t('onboarding.step3.theme') }}
            </p>
            <v-card variant="outlined" class="pa-2">
              <v-row>
                <v-col cols="6">
                  <v-card
                    :variant="modelValue.theme_preference === 'white' ? 'elevated' : 'outlined'"
                    :color="modelValue.theme_preference === 'white' ? 'primary' : undefined"
                    :data-selected="modelValue.theme_preference"
                    class="pa-3 text-center cursor-pointer theme-card"
                    @click="modelValue.theme_preference = 'white'"
                  >
                    <div class="theme-preview theme-white mb-2 mx-auto"></div>
                    <p class="text-body-2 font-weight-medium">{{ $t('onboarding.step3.themeWhite') }}</p>
                  </v-card>
                </v-col>
                <v-col cols="6">
                  <v-card
                    :variant="modelValue.theme_preference === 'black' ? 'elevated' : 'outlined'"
                    :color="modelValue.theme_preference === 'black' ? 'primary' : undefined"
                    :data-selected="modelValue.theme_preference"
                    class="pa-3 text-center cursor-pointer theme-card"
                    @click="modelValue.theme_preference = 'black'"
                  >
                    <div class="theme-preview theme-black mb-2 mx-auto"></div>
                    <p class="text-body-2 font-weight-medium">{{ $t('onboarding.step3.themeBlack') }}</p>
                  </v-card>
                </v-col>
              </v-row>
            </v-card>
          </v-col>

          <!-- Language Selection -->
          <v-col cols="12">
            <v-select
              v-model="modelValue.language_preference"
              :items="languageOptions"
              item-title="label"
              item-value="value"
:label="$t('onboarding.step3.language')"
              variant="outlined"
              prepend-inner-icon="mdi-web"
              density="comfortable"
              color="primary"
              class="rounded-lg"
              @update:model-value="updateLanguage"
            />
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
            @click="handleNext"
            color="secondary"
            size="large"
            block
            append-icon="mdi-arrow-right"
            class="rounded-pill font-weight-bold"
          >
            {{ $t('common.next') }}
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
  membership_due_day: number
  theme_preference: 'orbe-white' | 'orbe-black'
  language_preference: string
  // ... other fields
}

const props = defineProps<{
  modelValue: FormData
}>()

const emit = defineEmits<{
  next: []
  previous: []
}>()

const form = ref()
const { locale, t } = useI18n()

// Day options for membership
const dayOptions = computed(() => {
  return Array.from({ length: 28 }, (_, i) => ({
    value: i + 1,
    label: `${t('common.day')} ${i + 1}`
  }))
})

// Language options
const languageOptions = [
  { value: 'pt-br', label: '🇧🇷 Português (Brasil)' },
  { value: 'en', label: '🇺🇸 English' },
  { value: 'es', label: '🇪🇸 Español' }
]

function handleNext() {
  emit('next')
}

function updateLanguage() {
  locale.value = props.modelValue.language_preference
  localStorage.setItem('orbe-language', props.modelValue.language_preference)
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

.theme-card {
  transition: all 0.3s ease;
}

.theme-card:hover {
  transform: translateY(-2px);
}

.theme-preview {
  width: 32px;
  height: 20px;
  border-radius: 8px;
  border: 2px solid transparent;
  position: relative;
  transition: all 0.3s ease;
}

/* Tema Claro - Fundo claro */
.theme-white {
  background: linear-gradient(135deg, #DDEAF4 0%, #FFFFFF 100%);
  border-color: rgba(0, 0, 0, 0.1);
}

/* Tema Escuro - Fundo escuro */
.theme-black {
  background: linear-gradient(135deg, #304E69 0%, #5B7185 100%);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Indicador de seleção - checkmark */
.theme-preview::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #304E69;
  transition: transform 0.2s ease;
}

.theme-black::after {
  background: #FFFFFF;
}

/* Tema selecionado */
.theme-card[data-selected="white"] .theme-white {
  border-color: #304E69;
  box-shadow: 0 0 0 2px rgba(48, 78, 105, 0.2);
}

.theme-card[data-selected="white"] .theme-white::after {
  transform: translate(-50%, -50%) scale(1);
}

.theme-card[data-selected="black"] .theme-black {
  border-color: #C79657;
  box-shadow: 0 0 0 2px rgba(199, 150, 87, 0.2);
}

.theme-card[data-selected="black"] .theme-black::after {
  transform: translate(-50%, -50%) scale(1);
}

.cursor-pointer {
  cursor: pointer;
}

.rounded-lg :deep(.v-field) {
  border-radius: 12px;
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

  .theme-preview {
    width: 24px;
    height: 16px;
  }
}
</style>