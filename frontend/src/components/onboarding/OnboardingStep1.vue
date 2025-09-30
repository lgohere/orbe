<template>
  <div class="step-container">
    <!-- Header -->
    <div class="step-header pa-8 pb-4">
      <div class="text-center mb-4">
        <v-avatar size="48" color="secondary" class="mb-4">
          <v-icon size="24" color="white">mdi-account-circle</v-icon>
        </v-avatar>
        <h3 class="orbe-title text-h5 text-primary mb-2">
          {{ $t('onboarding.step1.title') }}
        </h3>
        <p class="orbe-body text-body-2 text-medium-emphasis">
          {{ $t('onboarding.step1.subtitle') }}
        </p>
      </div>
    </div>

    <!-- Form -->
    <v-card-text class="pa-8 pt-4">
      <v-form @submit.prevent="handleNext" ref="form">
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="modelValue.first_name"
              :label="$t('onboarding.step1.firstName')"
              :placeholder="$t('onboarding.step1.firstName')"
              variant="outlined"
              required
              prepend-inner-icon="mdi-account"
              density="comfortable"
              color="primary"
              :rules="[rules.required]"
              counter="50"
              maxlength="50"
              class="rounded-lg"
            />
          </v-col>

          <v-col cols="12">
            <v-text-field
              v-model="modelValue.last_name"
              :label="$t('onboarding.step1.lastName')"
              :placeholder="$t('onboarding.step1.lastName')"
              variant="outlined"
              required
              prepend-inner-icon="mdi-account"
              density="comfortable"
              color="primary"
              :rules="[rules.required]"
              counter="50"
              maxlength="50"
              class="rounded-lg"
            />
          </v-col>

          <v-col cols="12">
            <v-text-field
              v-model="modelValue.email"
              :label="$t('common.email')"
              :placeholder="$t('common.email')"
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

          <v-col cols="12">
            <div class="phone-input-container">
              <v-row no-gutters>
                <v-col cols="4" sm="3">
                  <v-select
                    v-model="selectedCountryCode"
                    :items="countryOptions"
                    item-title="label"
                    item-value="code"
                    variant="outlined"
                    density="comfortable"
                    color="primary"
                    class="country-select rounded-lg"
                    hide-details
                  >
                    <template v-slot:selection="{ item }">
                      <span class="country-selection">
                        {{ item.raw.flag }} {{ item.raw.code }}
                      </span>
                    </template>
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props" class="country-item">
                        <template v-slot:title>
                          <span>{{ item.raw.flag }} {{ item.raw.name }} {{ item.raw.code }}</span>
                        </template>
                      </v-list-item>
                    </template>
                  </v-select>
                </v-col>
                <v-col cols="8" sm="9">
                  <v-text-field
                    v-model="phoneNumber"
                    :label="$t('onboarding.step1.phone')"
                    :placeholder="getPhonePlaceholder()"
                    variant="outlined"
                    type="tel"
                    required
                    prepend-inner-icon="mdi-phone"
                    density="comfortable"
                    color="primary"
                    :rules="[rules.required, rules.phone]"
                    class="phone-number-input rounded-lg"
                    hide-details="auto"
                  />
                </v-col>
              </v-row>
            </div>
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
            :disabled="!isFormValid"
          >
            {{ $t('common.next') }}
          </v-btn>
        </v-col>
      </v-row>
    </v-card-actions>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

interface FormData {
  first_name: string
  last_name: string
  email: string
  phone: string
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
const { t, locale } = useI18n()

// Country code management
const selectedCountryCode = ref('+55')
const phoneNumber = ref('')

// Country options with flags and codes
const countryOptions = [
  { code: '+55', flag: '🇧🇷', name: 'Brasil' },
  { code: '+1', flag: '🇺🇸', name: 'USA' },
  { code: '+34', flag: '🇪🇸', name: 'España' },
  { code: '+972', flag: '🇮🇱', name: 'Israel' },
  { code: '+33', flag: '🇫🇷', name: 'France' },
  { code: '+49', flag: '🇩🇪', name: 'Germany' },
  { code: '+44', flag: '🇬🇧', name: 'UK' },
  { code: '+39', flag: '🇮🇹', name: 'Italy' },
  { code: '+351', flag: '🇵🇹', name: 'Portugal' },
  { code: '+54', flag: '🇦🇷', name: 'Argentina' },
  { code: '+52', flag: '🇲🇽', name: 'México' }
]

// Initialize phone number from existing data
if (props.modelValue.phone) {
  // Extract country code and number from existing phone
  const phone = props.modelValue.phone
  for (const country of countryOptions) {
    const code = country.code.replace('+', '')
    if (phone.startsWith(code)) {
      selectedCountryCode.value = country.code
      phoneNumber.value = phone.substring(code.length)
      break
    }
  }
}

// Watch for language changes to auto-select country code
watch(locale, (newLocale) => {
  // Only auto-select if no phone number is already set
  if (!phoneNumber.value) {
    if (newLocale === 'pt-BR') {
      selectedCountryCode.value = '+55'
    } else if (newLocale === 'en') {
      selectedCountryCode.value = '+1'
    } else if (newLocale === 'es') {
      selectedCountryCode.value = '+34'
    }
  }
}, { immediate: true })

// Watch for changes to update the complete phone in modelValue
watch([selectedCountryCode, phoneNumber], ([newCode, newNumber]) => {
  if (newNumber) {
    props.modelValue.phone = newCode.replace('+', '') + newNumber
  } else {
    props.modelValue.phone = ''
  }
})

// Get phone placeholder based on selected country
function getPhonePlaceholder() {
  switch (selectedCountryCode.value) {
    case '+55':
      return '(11) 99999-9999'
    case '+1':
      return '(555) 123-4567'
    case '+34':
      return '612 345 678'
    case '+972':
      return '050-123-4567'
    default:
      return '123456789'
  }
}

// Validation rules
const rules = {
  required: (value: string) => !!value || t('common.required'),
  email: (value: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || t('validation.email')
  },
  phone: (value: string) => {
    const pattern = /^[\(\)\s\-\d]{8,15}$/
    return pattern.test(value) || t('validation.phone')
  }
}

// Computed property to check form validity
const isFormValid = computed(() => {
  return props.modelValue.first_name?.length > 0 &&
         props.modelValue.last_name?.length > 0 &&
         props.modelValue.email?.length > 0 &&
         phoneNumber.value?.length >= 8
})

async function handleNext() {
  const { valid } = await form.value.validate()
  if (valid) {
    emit('next')
  }
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

.rounded-lg :deep(.v-field) {
  border-radius: 12px;
}

.rounded-pill {
  border-radius: 28px;
}

/* Phone input styling */
.phone-input-container .country-select :deep(.v-field) {
  border-top-right-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
  border-right: none !important;
}

.phone-input-container .phone-number-input :deep(.v-field) {
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
}

.country-selection {
  font-size: 0.875rem;
  font-weight: 500;
}

.country-item {
  font-size: 0.875rem;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .pa-8 {
    padding: 1.5rem !important;
  }

  .step-header {
    padding: 1.5rem 1.5rem 1rem !important;
  }

  .country-selection {
    font-size: 0.75rem;
  }
}
</style>