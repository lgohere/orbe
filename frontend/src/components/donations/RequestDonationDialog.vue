<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="700">
    <v-card>
      <v-card-title class="text-h5">
        <v-icon icon="mdi-hand-heart" color="secondary" class="mr-2" />
        {{ editRequest ? $t('donations.editRequest') : $t('donations.requestDonation') }}
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="formValid" @submit.prevent="submit">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.recipient_name"
                :label="$t('donations.recipientName')"
                :rules="[rules.required]"
                variant="outlined"
                required
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model.number="form.amount"
                :label="$t('donations.estimatedAmount')"
                type="number"
                step="0.01"
                min="10"
                prefix="R$"
                :rules="[rules.required, rules.minAmount]"
                variant="outlined"
                required
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="form.recipient_description"
                :label="$t('donations.recipientDescription')"
                :rules="[rules.required]"
                rows="3"
                variant="outlined"
                counter="500"
                required
              />
              <p class="text-caption text-medium-emphasis">
                {{ $t('donations.recipientDescriptionHelpText') }}
              </p>
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="form.reason"
                :label="$t('donations.reasonForNeed')"
                :rules="[rules.required]"
                rows="4"
                variant="outlined"
                counter="1000"
                required
              />
              <p class="text-caption text-medium-emphasis">
                {{ $t('donations.reasonHelpText') }}
              </p>
            </v-col>

            <v-col cols="12">
              <v-select
                v-model="form.urgency_level"
                :label="$t('donations.urgencyLevel')"
                :items="urgencyOptions"
                :rules="[rules.required]"
                variant="outlined"
                required
              />
            </v-col>

            <v-col cols="12">
              <v-alert type="info" variant="tonal" density="compact">
                <strong>{{ $t('donations.importantNote') }}:</strong>
                {{ $t('donations.requestWillBeReviewed') }}
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
          @click="closeDialog"
          :disabled="loading"
        >
          {{ $t('common.cancel') }}
        </v-btn>
        <v-btn
          color="secondary"
          variant="flat"
          :loading="loading"
          :disabled="!formValid"
          @click="submit"
        >
          {{ editRequest ? $t('common.update') : $t('common.submit') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { apiService, type DonationRequest } from '@/services/api'

const props = defineProps<{
  modelValue: boolean
  editRequest?: DonationRequest | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
  close: []
}>()

const formRef = ref()
const formValid = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

const form = reactive({
  recipient_name: '',
  recipient_description: '',
  amount: 0,
  reason: '',
  urgency_level: 'medium' as 'low' | 'medium' | 'high' | 'critical',
})

const urgencyOptions = [
  { value: 'low', title: 'Baixa' },
  { value: 'medium', title: 'Média' },
  { value: 'high', title: 'Alta' },
  { value: 'critical', title: 'Crítica' },
]

const rules = {
  required: (v: any) => !!v || 'Campo obrigatório',
  minAmount: (v: number) => v >= 10 || 'Valor mínimo: R$ 10,00',
}

const submit = async () => {
  if (!formValid.value) return

  loading.value = true
  error.value = null

  try {
    let response

    if (props.editRequest) {
      response = await apiService.updateDonationRequest(props.editRequest.id, form)
    } else {
      response = await apiService.createDonationRequest(form)
    }

    if (response.error) {
      error.value = response.error
    } else {
      emit('success')
      closeDialog()
    }
  } catch (err) {
    error.value = 'Falha ao salvar solicitação'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.recipient_name = ''
  form.recipient_description = ''
  form.amount = 0
  form.reason = ''
  form.urgency_level = 'medium'
  error.value = null
  formRef.value?.reset()
}

const loadEditData = () => {
  if (props.editRequest) {
    form.recipient_name = props.editRequest.recipient_name
    form.recipient_description = props.editRequest.recipient_description
    form.amount = props.editRequest.amount
    form.reason = props.editRequest.reason
    form.urgency_level = props.editRequest.urgency_level
  }
}

const closeDialog = () => {
  emit('update:modelValue', false)
  emit('close')
  resetForm()
}

watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    if (props.editRequest) {
      loadEditData()
    } else {
      resetForm()
    }
  }
})
</script>
