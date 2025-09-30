<template>
  <div class="step-container">
    <!-- Header -->
    <div class="step-header pa-8 pb-4">
      <div class="text-center mb-4">
        <v-avatar size="48" color="secondary" class="mb-4">
          <v-icon size="24" color="white">mdi-home-map-marker</v-icon>
        </v-avatar>
        <h3 class="orbe-title text-h5 text-primary mb-2">
          {{ $t('onboarding.step2.title') }}
        </h3>
        <p class="orbe-body text-body-2 text-medium-emphasis">
          {{ $t('onboarding.step2.subtitle') }}
        </p>
      </div>
    </div>

    <!-- Form -->
    <v-card-text class="pa-8 pt-4">
      <v-form @submit.prevent="handleNext" ref="form">
        <v-row>
          <!-- Auto-detect button -->
          <v-col cols="12" class="text-center mb-4">
            <v-btn
              @click="detectCurrentLocation"
              :loading="isDetectingLocation"
              color="secondary"
              size="large"
              prepend-icon="mdi-crosshairs-gps"
              class="rounded-pill font-weight-medium"
              variant="elevated"
            >
              {{ $t('onboarding.step2.detectLocation') }}
            </v-btn>
            <p class="text-caption text-medium-emphasis mt-2">
              {{ $t('onboarding.step2.detectLocationHint') }}
            </p>
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model="modelValue.city"
              :label="$t('onboarding.step2.city')"
              :placeholder="$t('onboarding.step2.cityPlaceholder')"
              variant="outlined"
              required
              prepend-inner-icon="mdi-city"
              density="comfortable"
              color="primary"
              :rules="[rules.required]"
              class="rounded-lg"
            />
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model="modelValue.state"
              :label="$t('onboarding.step2.state')"
              :placeholder="$t('onboarding.step2.statePlaceholder')"
              variant="outlined"
              required
              prepend-inner-icon="mdi-map"
              density="comfortable"
              color="primary"
              :rules="[rules.required]"
              class="rounded-lg"
            />
          </v-col>

          <v-col cols="12">
            <v-text-field
              v-model="modelValue.country"
              :label="$t('onboarding.step2.country')"
              :placeholder="$t('onboarding.step2.countryPlaceholder')"
              variant="outlined"
              required
              prepend-inner-icon="mdi-earth"
              density="comfortable"
              color="primary"
              :rules="[rules.required]"
              class="rounded-lg"
            />
          </v-col>

          <!-- Error/Success messages -->
          <v-col cols="12" v-if="locationMessage">
            <v-alert
              :type="locationMessageType"
              variant="tonal"
              density="compact"
              class="rounded-lg"
            >
              {{ locationMessage }}
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
  city: string
  state: string
  country: string
  location_place_id?: string
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
const { t } = useI18n()

// Location detection state
const isDetectingLocation = ref(false)
const locationMessage = ref('')
const locationMessageType = ref<'success' | 'error' | 'info'>('info')

// Auto-detect current location using browser geolocation
async function detectCurrentLocation() {
  if (!navigator.geolocation) {
    showLocationMessage(t('onboarding.step2.geolocationNotSupported'), 'error')
    return
  }

  isDetectingLocation.value = true
  locationMessage.value = ''

  try {
    const position = await new Promise<GeolocationPosition>((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes cache
      })
    })

    // Use reverse geocoding with OpenStreetMap (free)
    const { latitude, longitude } = position.coords
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?` +
      `lat=${latitude}&lon=${longitude}&` +
      `format=json&addressdetails=1&accept-language=pt-BR`
    )

    if (!response.ok) throw new Error('Reverse geocoding failed')

    const data = await response.json()
    const address = data.address || {}

    // Extract location information
    const city = address.city ||
                address.town ||
                address.village ||
                address.municipality ||
                ''

    const state = address.state ||
                 address.region ||
                 address.province ||
                 ''

    const country = address.country || ''

    if (city && country) {
      // Fill the form fields
      props.modelValue.city = city
      props.modelValue.state = state
      props.modelValue.country = country

      showLocationMessage(
        t('onboarding.step2.locationDetectedSuccess', { city, country }),
        'success'
      )
    } else {
      throw new Error('Incomplete location data')
    }

  } catch (error) {
    console.error('Geolocation error:', error)

    if (error instanceof GeolocationPositionError) {
      switch (error.code) {
        case GeolocationPositionError.PERMISSION_DENIED:
          showLocationMessage(t('onboarding.step2.locationPermissionDenied'), 'error')
          break
        case GeolocationPositionError.POSITION_UNAVAILABLE:
          showLocationMessage(t('onboarding.step2.locationUnavailable'), 'error')
          break
        case GeolocationPositionError.TIMEOUT:
          showLocationMessage(t('onboarding.step2.locationTimeout'), 'error')
          break
      }
    } else {
      showLocationMessage(t('onboarding.step2.locationDetectionFailed'), 'error')
    }
  } finally {
    isDetectingLocation.value = false
  }
}

// Show location message with auto-hide
function showLocationMessage(message: string, type: 'success' | 'error' | 'info') {
  locationMessage.value = message
  locationMessageType.value = type

  // Auto-hide after 5 seconds
  setTimeout(() => {
    locationMessage.value = ''
  }, 5000)
}

// Initialize with empty values if not already set
if (!props.modelValue.city) props.modelValue.city = ''
if (!props.modelValue.state) props.modelValue.state = ''
if (!props.modelValue.country) props.modelValue.country = ''

// Validation rules
const rules = {
  required: (value: string) => !!value || t('common.required')
}

// Computed property to check form validity
const isFormValid = computed(() => {
  return props.modelValue.city?.length > 0 &&
         props.modelValue.state?.length > 0 &&
         props.modelValue.country?.length > 0
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