<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="600" persistent>
    <v-card rounded="lg">
      <!-- Header -->
      <v-card-title class="bg-success text-white pa-6">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon icon="mdi-hand-heart" size="32" class="mr-3" />
            <div>
              <div class="text-h5 font-weight-bold">{{ $t('donations.makeVoluntaryDonation') }}</div>
              <div class="text-caption text-white text-opacity-80">Apoie a missão da ORBE</div>
            </div>
          </div>
          <v-btn
            icon="mdi-close"
            variant="text"
            color="white"
            @click="$emit('update:modelValue', false)"
            :disabled="loading"
          />
        </div>
      </v-card-title>

      <v-card-text class="pa-6">
        <!-- Info Alert -->
        <v-alert
          type="info"
          variant="tonal"
          density="compact"
          class="mb-6"
        >
          <div class="text-body-2">
            Sua doação espontânea ajuda a ORBE a continuar transformando vidas.
            O comprovante de pagamento é obrigatório para validação. 💙
          </div>
        </v-alert>

        <v-form ref="formRef" v-model="formValid" @submit.prevent="submit">
          <!-- Amount Field -->
          <v-text-field
            v-model="formattedAmount"
            :label="$t('donations.amount')"
            prefix="R$"
            :rules="[rules.required, rules.minAmount]"
            variant="outlined"
            density="comfortable"
            class="mb-4"
            placeholder="0,00"
            required
            @input="formatCurrency"
            @blur="addDecimalPlaces"
          />

          <!-- Message Field -->
          <v-textarea
            v-model="form.message"
            :label="$t('donations.message') + ' (' + $t('common.optional') + ')'"
            placeholder="Deixe uma mensagem de apoio..."
            rows="3"
            variant="outlined"
            density="comfortable"
            counter="500"
            :rules="[rules.maxLength(500)]"
            hint="Sua mensagem pode aparecer no feed para inspirar outros membros"
            persistent-hint
            class="mb-4"
          />

          <!-- Anonymous Checkbox -->
          <v-checkbox
            v-model="form.is_anonymous"
            :label="$t('donations.makeAnonymous')"
            color="success"
            class="mb-4"
          >
            <template #append>
              <v-tooltip location="top">
                <template #activator="{ props }">
                  <v-icon
                    v-bind="props"
                    icon="mdi-information-outline"
                    size="small"
                    color="grey"
                  />
                </template>
                <span>{{ $t('donations.anonymousHelpText') }}</span>
              </v-tooltip>
            </template>
          </v-checkbox>

          <v-divider class="mb-4" />

          <!-- Payment Proof Upload -->
          <div class="mb-4">
            <div class="text-subtitle-2 font-weight-bold mb-2">
              <v-icon icon="mdi-paperclip" size="small" class="mr-1" />
              Comprovante de Pagamento *
            </div>
            <v-file-input
              v-model="form.payment_proof"
              accept="image/*,application/pdf"
              prepend-icon="mdi-file-upload"
              variant="outlined"
              density="comfortable"
              :rules="[rules.required, rules.fileSize]"
              show-size
              placeholder="Anexe o comprovante do PIX ou transferência"
              required
              class="mb-2"
            />
            <p class="text-caption text-medium-emphasis ml-1">
              {{ $t('donations.paymentProofHelpText') }}
            </p>
          </div>

          <!-- PIX QR Code Section -->
          <v-divider class="mb-4" />

          <div>
            <div class="text-subtitle-2 font-weight-bold mb-3">
              <v-icon icon="mdi-qrcode" size="small" class="mr-1" />
              {{ $t('donations.pixInstructions') }}
            </div>

            <v-alert type="info" variant="tonal">
              <!-- QR Code Toggle -->
              <div class="d-flex align-center justify-space-between mb-3">
                <span class="text-body-2 font-weight-medium">QR Code PIX</span>
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="showQrCode = !showQrCode"
                  :append-icon="showQrCode ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                >
                  {{ showQrCode ? 'Ocultar' : 'Mostrar' }}
                </v-btn>
              </div>

              <!-- QR Code Image -->
              <v-expand-transition>
                <div v-show="showQrCode" class="text-center mb-4">
                  <img
                    src="/qrcode-Orbe-Mensalidade-pix.png"
                    alt="QR Code PIX ORBE"
                    style="max-width: 220px; width: 100%; height: auto; border-radius: 12px;"
                    class="qr-code-img mx-auto"
                  />
                  <p class="text-caption text-medium-emphasis mt-2">
                    Escaneie com o app do seu banco
                  </p>
                </div>
              </v-expand-transition>

              <!-- PIX Key -->
              <div class="mb-3">
                <div class="text-caption text-medium-emphasis mb-1">Chave PIX:</div>
                <div class="text-body-2 font-weight-medium">
                  <v-icon icon="mdi-domain" size="small" class="mr-1" />
                  46.005.417/0001-48
                </div>
              </div>

              <!-- PIX Code Copy Card -->
              <div>
                <div class="text-caption text-medium-emphasis mb-2 text-center">Código PIX Copia e Cola:</div>
                <v-card
                  variant="outlined"
                  class="pa-4 pix-code-card mx-auto"
                  @click="copyPixCode"
                  style="cursor: pointer; max-width: 90%;"
                  elevation="0"
                >
                  <div class="d-flex align-center justify-center gap-3">
                    <div class="pix-code-text text-caption font-mono text-center flex-1">
                      {{ pixCode }}
                    </div>
                    <v-btn
                      icon="mdi-content-copy"
                      variant="tonal"
                      color="success"
                      size="small"
                      @click.stop="copyPixCode"
                    />
                  </div>
                </v-card>
                <p class="text-caption text-medium-emphasis text-center mt-2">
                  <v-icon icon="mdi-hand-pointing-up" size="small" class="mr-1" />
                  Clique no código acima para copiar
                </p>
              </div>
            </v-alert>
          </div>
        </v-form>

        <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>

      <!-- Actions -->
      <v-divider />
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="grey-darken-1"
          variant="text"
          @click="$emit('update:modelValue', false)"
          :disabled="loading"
        >
          {{ $t('common.cancel') }}
        </v-btn>
        <v-btn
          color="success"
          variant="flat"
          prepend-icon="mdi-hand-heart"
          :loading="loading"
          :disabled="!formValid"
          @click="submit"
          size="large"
        >
          {{ $t('donations.submitDonation') }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Success Toast for PIX Code Copy -->
    <v-snackbar
      v-model="showCopiedToast"
      :timeout="3000"
      color="success"
      location="top"
    >
      <div class="d-flex align-center">
        <v-icon icon="mdi-check-circle" class="mr-2" />
        Código PIX copiado com sucesso!
      </div>
    </v-snackbar>
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
const showQrCode = ref(false)
const showCopiedToast = ref(false)
const formattedAmount = ref('')

const pixCode = '00020126360014BR.GOV.BCB.PIX011446005417000148520400005303986540560.005802BR5901N6001C62190515OrbeMensalidade63044975'

const form = reactive({
  amount: 0,
  message: '',
  is_anonymous: false,
  payment_proof: null as File[] | null,
})

const rules = {
  required: (v: any) => {
    if (Array.isArray(v)) return v.length > 0 || 'Campo obrigatório'
    return !!v || 'Campo obrigatório'
  },
  minAmount: (v: number) => v >= 1 || 'Valor mínimo: R$ 1,00',
  maxLength: (max: number) => (v: string) =>
    !v || v.length <= max || `Máximo ${max} caracteres`,
  fileSize: (v: File[] | null) => {
    if (!v || v.length === 0) return 'Comprovante de pagamento é obrigatório'
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
  formattedAmount.value = ''
  form.message = ''
  form.is_anonymous = false
  form.payment_proof = null
  error.value = null
  showQrCode.value = false
  formRef.value?.reset()
}

function formatCurrency(event: any) {
  let value = event.target.value

  // Remove tudo exceto números e vírgula
  value = value.replace(/[^\d,]/g, '')

  // Remove vírgulas extras
  const parts = value.split(',')
  if (parts.length > 2) {
    value = parts[0] + ',' + parts.slice(1).join('')
  }

  // Limita casas decimais a 2
  if (parts.length === 2 && parts[1].length > 2) {
    value = parts[0] + ',' + parts[1].substring(0, 2)
  }

  formattedAmount.value = value

  // Atualiza o valor numérico no form
  const cleanValue = value.replace(',', '.')
  form.amount = parseFloat(cleanValue) || 0
}

function addDecimalPlaces() {
  if (!formattedAmount.value) return

  let value = formattedAmount.value

  // Se não tem vírgula, adiciona ,00
  if (!value.includes(',')) {
    value = value + ',00'
  } else {
    // Se tem vírgula mas falta casas decimais
    const parts = value.split(',')
    if (parts[1].length === 0) {
      value = parts[0] + ',00'
    } else if (parts[1].length === 1) {
      value = parts[0] + ',' + parts[1] + '0'
    }
  }

  formattedAmount.value = value

  // Atualiza o valor numérico no form
  const cleanValue = value.replace(',', '.')
  form.amount = parseFloat(cleanValue) || 0
}

async function copyPixCode() {
  try {
    await navigator.clipboard.writeText(pixCode)
    showCopiedToast.value = true
  } catch (error) {
    console.error('Failed to copy PIX code:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = pixCode
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      showCopiedToast.value = true
    } catch (err) {
      console.error('Fallback copy failed:', err)
    }
    document.body.removeChild(textArea)
  }
}

watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    resetForm()
  }
})
</script>

<style scoped>
/* QR Code Image */
.qr-code-img {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.qr-code-img:hover {
  transform: scale(1.03);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* PIX Code Card */
.pix-code-card {
  transition: all 0.2s ease;
  background-color: rgba(var(--v-theme-surface), 0.5);
}

.pix-code-card:hover {
  background-color: rgba(var(--v-theme-success), 0.08);
  border-color: rgb(var(--v-theme-success));
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* PIX Code Text */
.pix-code-text {
  word-break: break-all;
  line-height: 1.5;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.7rem;
  color: rgba(var(--v-theme-on-surface), 0.8);
}

.font-mono {
  font-family: 'Courier New', Courier, monospace;
}

/* Gap utility */
.gap-2 {
  gap: 0.5rem;
}

.gap-3 {
  gap: 0.75rem;
}

/* Consistent spacing */
:deep(.v-field) {
  border-radius: 8px;
}

:deep(.v-alert) {
  border-radius: 8px;
}

/* Center PIX code card */
.mx-auto {
  margin-left: auto;
  margin-right: auto;
}

/* Remove duplicate R$ symbol */
:deep(.v-field__prepend-inner .v-icon) {
  opacity: 0.7;
}
</style>
