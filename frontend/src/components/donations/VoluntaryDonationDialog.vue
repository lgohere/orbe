<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="600">
    <v-card>
      <v-card-title class="text-h5">
        <v-icon icon="mdi-heart" color="primary" class="mr-2" />
        {{ $t('donations.makeVoluntaryDonation') }}
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="formValid" @submit.prevent="submit">
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model.number="form.amount"
                :label="$t('donations.amount')"
                type="number"
                step="0.01"
                min="1"
                prefix="R$"
                :rules="[rules.required, rules.minAmount]"
                variant="outlined"
                required
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="form.message"
                :label="$t('donations.message') + ' (' + $t('common.optional') + ')'"
                rows="3"
                variant="outlined"
                counter="500"
                :rules="[rules.maxLength(500)]"
              />
            </v-col>

            <v-col cols="12">
              <v-checkbox
                v-model="form.is_anonymous"
                :label="$t('donations.makeAnonymous')"
                hide-details
              />
              <p class="text-caption text-medium-emphasis ml-8">
                {{ $t('donations.anonymousHelpText') }}
              </p>
            </v-col>

            <v-col cols="12">
              <v-file-input
                v-model="form.payment_proof"
                :label="$t('donations.paymentProof') + ' (' + $t('common.optional') + ')'"
                accept="image/*,application/pdf"
                prepend-icon="mdi-file-upload"
                variant="outlined"
                :rules="[rules.fileSize]"
                show-size
              />
              <p class="text-caption text-medium-emphasis">
                {{ $t('donations.paymentProofHelpText') }}
              </p>
            </v-col>

            <!-- PIX QR Code Placeholder -->
            <v-col cols="12">
              <v-alert type="info" variant="tonal" class="mb-0">
                <strong>{{ $t('donations.pixInstructions') }}</strong>
                <p class="mt-2">
                  {{ $t('donations.pixKey') }}: <code>donations@orbe.org.br</code>
                </p>
                <!-- TODO: Generate and display QR Code -->
                <div class="text-center mt-4">
                  <v-btn color="primary" variant="outlined" prepend-icon="mdi-qrcode">
                    {{ $t('donations.showQrCode') }}
                  </v-btn>
                </div>
              </v-alert>
            </v-col>
          </v-row>
        </v-form>

        <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          @click="$emit('update:modelValue', false)"
          :disabled="loading"
        >
          {{ $t('common.cancel') }}
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :loading="loading"
          :disabled="!formValid"
          @click="submit"
        >
          {{ $t('donations.submitDonation') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { apiService } from '@/services/api'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const formRef = ref()
const formValid = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

const form = reactive({
  amount: 0,
  message: '',
  is_anonymous: false,
  payment_proof: null as File[] | null,
})

const rules = {
  required: (v: any) => !!v || 'Campo obrigatório',
  minAmount: (v: number) => v >= 1 || 'Valor mínimo: R$ 1,00',
  maxLength: (max: number) => (v: string) =>
    !v || v.length <= max || `Máximo ${max} caracteres`,
  fileSize: (v: File[] | null) => {
    if (!v || v.length === 0) return true
    const file = v[0]
    return file.size <= 5 * 1024 * 1024 || 'Arquivo muito grande (máx 5MB)'
  },
}

const submit = async () => {
  if (!formValid.value) return

  loading.value = true
  error.value = null

  try {
    const response = await apiService.createVoluntaryDonation({
      amount: form.amount,
      message: form.message || undefined,
      is_anonymous: form.is_anonymous,
      payment_proof: form.payment_proof?.[0],
    })

    if (response.error) {
      error.value = response.error
    } else {
      emit('success')
      resetForm()
    }
  } catch (err) {
    error.value = 'Falha ao registrar doação'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.amount = 0
  form.message = ''
  form.is_anonymous = false
  form.payment_proof = null
  error.value = null
  formRef.value?.reset()
}

watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    resetForm()
  }
})
</script>
