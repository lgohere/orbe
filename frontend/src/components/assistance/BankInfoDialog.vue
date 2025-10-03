<template>
  <v-dialog v-model="dialog" max-width="700" persistent>
    <v-card>
      <v-card-title class="text-h5 bg-blue-grey text-white">
        <v-icon class="mr-2">mdi-bank</v-icon>
        Informar Dados Bancários do Beneficiário
      </v-card-title>

      <v-card-text class="pt-6">
        <v-alert type="info" variant="tonal" class="mb-4">
          <div class="text-body-2">
            Por favor, informe os dados bancários do beneficiário da doação.
            O admin precisará dessas informações para realizar a transferência.
          </div>
        </v-alert>

        <v-form ref="formRef" v-model="valid">
          <!-- Beneficiary Name -->
          <v-text-field
            v-model="form.beneficiary_name"
            label="Nome Completo do Beneficiário *"
            prepend-icon="mdi-account"
            variant="outlined"
            :rules="[rules.required]"
            required
          />

          <!-- Beneficiary CPF -->
          <v-text-field
            v-model="form.beneficiary_cpf"
            label="CPF do Beneficiário *"
            prepend-icon="mdi-card-account-details"
            placeholder="000.000.000-00"
            variant="outlined"
            :rules="[rules.required, rules.cpf]"
            required
            @input="formatCPF"
          />

          <v-divider class="my-6" />

          <div class="text-subtitle-1 font-weight-bold mb-4">
            Escolha uma das opções abaixo:
          </div>

          <!-- Option 1: PIX -->
          <v-card variant="outlined" class="mb-4" :class="{ 'border-primary': hasPixKey }">
            <v-card-title class="text-body-1 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-qrcode</v-icon>
              Opção 1: Chave PIX (Recomendado)
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="form.beneficiary_pix_key"
                label="Chave PIX"
                prepend-icon="mdi-key"
                placeholder="CPF, e-mail, telefone ou chave aleatória"
                variant="outlined"
                hint="Forma mais rápida e segura de transferência"
                persistent-hint
                @input="onPixKeyChange"
              />
            </v-card-text>
          </v-card>

          <!-- Option 2: Full Bank Info -->
          <v-card variant="outlined" :class="{ 'border-primary': hasBankInfo }">
            <v-card-title class="text-body-1 bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-bank-outline</v-icon>
              Opção 2: Dados Bancários Completos
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="form.beneficiary_bank"
                label="Nome do Banco"
                prepend-icon="mdi-bank"
                placeholder="Ex: Banco do Brasil, Caixa, Nubank"
                variant="outlined"
                @input="onBankInfoChange"
              />

              <v-select
                v-model="form.beneficiary_account_type"
                :items="accountTypes"
                label="Tipo de Conta"
                prepend-icon="mdi-credit-card-outline"
                variant="outlined"
                @update:model-value="onBankInfoChange"
              />

              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="form.beneficiary_agency"
                    label="Agência"
                    prepend-icon="mdi-office-building"
                    placeholder="1234"
                    variant="outlined"
                    @input="onBankInfoChange"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="form.beneficiary_account"
                    label="Conta com Dígito"
                    prepend-icon="mdi-numeric"
                    placeholder="12345-6"
                    variant="outlined"
                    @input="onBankInfoChange"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <v-alert v-if="!hasPixKey && !hasBankInfo" type="warning" variant="tonal" class="mt-4">
            Por favor, preencha a Chave PIX OU os dados bancários completos (Banco, Agência e Conta).
          </v-alert>
        </v-form>
      </v-card-text>

      <v-card-actions class="px-6 pb-4">
        <v-spacer />
        <v-btn
          variant="text"
          @click="closeDialog"
          :disabled="loading"
        >
          Cancelar
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          prepend-icon="mdi-send"
          @click="submitBankInfo"
          :loading="loading"
          :disabled="!canSubmit"
        >
          Enviar Dados Bancários
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

interface BankInfoForm {
  beneficiary_name: string
  beneficiary_cpf: string
  beneficiary_pix_key: string
  beneficiary_bank: string
  beneficiary_account_type: string
  beneficiary_agency: string
  beneficiary_account: string
}

const props = defineProps<{
  modelValue: boolean
  caseId: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'submitted': []
}>()

const authStore = useAuthStore()
const formRef = ref<any>(null)
const valid = ref(false)
const loading = ref(false)

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const form = ref<BankInfoForm>({
  beneficiary_name: '',
  beneficiary_cpf: '',
  beneficiary_pix_key: '',
  beneficiary_bank: '',
  beneficiary_account_type: '',
  beneficiary_agency: '',
  beneficiary_account: ''
})

const accountTypes = [
  { title: 'Conta Corrente', value: 'corrente' },
  { title: 'Conta Poupança', value: 'poupanca' },
  { title: 'Conta Pagamento', value: 'pagamento' }
]

const rules = {
  required: (v: string) => !!v || 'Campo obrigatório',
  cpf: (v: string) => {
    if (!v) return 'CPF é obrigatório'
    const cleaned = v.replace(/\D/g, '')
    return cleaned.length === 11 || 'CPF deve ter 11 dígitos'
  }
}

const hasPixKey = computed(() => !!form.value.beneficiary_pix_key.trim())
const hasBankInfo = computed(() => 
  !!form.value.beneficiary_bank.trim() &&
  !!form.value.beneficiary_agency.trim() &&
  !!form.value.beneficiary_account.trim()
)

const canSubmit = computed(() => {
  return valid.value && 
         form.value.beneficiary_name.trim() &&
         form.value.beneficiary_cpf.trim() &&
         (hasPixKey.value || hasBankInfo.value)
})

function formatCPF() {
  let value = form.value.beneficiary_cpf.replace(/\D/g, '')
  if (value.length > 11) value = value.substring(0, 11)
  
  if (value.length > 9) {
    value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  } else if (value.length > 6) {
    value = value.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3')
  } else if (value.length > 3) {
    value = value.replace(/(\d{3})(\d{1,3})/, '$1.$2')
  }
  
  form.value.beneficiary_cpf = value
}

function onPixKeyChange() {
  // If PIX key is entered, clear bank info fields
  if (hasPixKey.value) {
    form.value.beneficiary_bank = ''
    form.value.beneficiary_account_type = ''
    form.value.beneficiary_agency = ''
    form.value.beneficiary_account = ''
  }
}

function onBankInfoChange() {
  // If bank info is entered, clear PIX key
  if (hasBankInfo.value) {
    form.value.beneficiary_pix_key = ''
  }
}

async function submitBankInfo() {
  if (!formRef.value) return
  
  const { valid: isValid } = await formRef.value.validate()
  if (!isValid || !canSubmit.value) return

  loading.value = true

  try {
    const response = await fetch(`/api/assistance/cases/${props.caseId}/submit_bank_info/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })

    if (!response.ok) {
      const data = await response.json()
      const errorMessage = typeof data === 'object' 
        ? Object.values(data).flat().join(', ') 
        : 'Erro ao enviar dados bancários'
      throw new Error(errorMessage)
    }

    // Success
    emit('submitted')
    closeDialog()
    resetForm()
  } catch (error: any) {
    console.error('Error submitting bank info:', error)
    alert(error.message || 'Erro ao enviar dados bancários. Por favor, tente novamente.')
  } finally {
    loading.value = false
  }
}

function closeDialog() {
  dialog.value = false
}

function resetForm() {
  form.value = {
    beneficiary_name: '',
    beneficiary_cpf: '',
    beneficiary_pix_key: '',
    beneficiary_bank: '',
    beneficiary_account_type: '',
    beneficiary_agency: '',
    beneficiary_account: ''
  }
  formRef.value?.resetValidation()
}

// Reset form when dialog closes
watch(dialog, (newValue) => {
  if (!newValue) {
    setTimeout(resetForm, 300)
  }
})
</script>

<style scoped>
.border-primary {
  border: 2px solid rgb(var(--v-theme-primary)) !important;
}
</style>
