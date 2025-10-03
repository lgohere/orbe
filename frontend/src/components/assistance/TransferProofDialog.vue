<template>
  <v-dialog v-model="isOpen" max-width="600" persistent>
    <v-card v-if="props.caseData">
      <v-card-title class="d-flex align-center bg-info">
        <v-icon class="mr-2" color="white">mdi-bank-transfer</v-icon>
        <span class="text-white">Confirmar Transferência</span>
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" color="white" @click="close" :disabled="uploading" />
      </v-card-title>

      <v-card-text class="pt-6">
        <v-alert type="info" variant="tonal" class="mb-4">
          <div class="text-body-2">
            <strong>Instruções:</strong>
            <ul class="mt-2 ml-4">
              <li>Transfira o valor de <strong>R$ {{ formatCurrency(caseData?.total_value) }}</strong> para o membro</li>
              <li>Use os dados bancários fornecidos pelo membro</li>
              <li>Faça upload do comprovante (PIX ou transferência bancária)</li>
              <li>Formatos aceitos: PDF, JPG, PNG (máx. 5MB)</li>
            </ul>
          </div>
        </v-alert>

        <!-- Dados Bancários do Beneficiário -->
        <v-card variant="outlined" class="mb-4">
          <v-card-title class="text-subtitle-1 bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-account-cash</v-icon>
            Dados Bancários do Beneficiário
          </v-card-title>
          <v-card-text>
            <v-row dense>
              <v-col cols="12">
                <div class="text-caption text-grey">Nome</div>
                <div class="text-body-1 font-weight-bold">{{ caseData?.beneficiary_name }}</div>
              </v-col>
              <v-col cols="12">
                <div class="text-caption text-grey">CPF</div>
                <div class="text-body-1">{{ caseData?.beneficiary_cpf }}</div>
              </v-col>

              <!-- PIX Key (if provided) -->
              <v-col v-if="caseData?.beneficiary_pix_key" cols="12">
                <div class="text-caption text-grey">Chave PIX</div>
                <div class="text-body-1 font-weight-medium text-primary">
                  {{ caseData?.beneficiary_pix_key }}
                  <v-btn
                    icon="mdi-content-copy"
                    variant="text"
                    size="small"
                    @click="copyToClipboard(caseData.beneficiary_pix_key)"
                  />
                </div>
              </v-col>

              <!-- Bank Details (if provided) -->
              <template v-if="caseData?.beneficiary_bank">
                <v-col cols="6">
                  <div class="text-caption text-grey">Banco</div>
                  <div class="text-body-1">{{ caseData?.beneficiary_bank }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption text-grey">Tipo de Conta</div>
                  <div class="text-body-1">{{ formatAccountType(caseData?.beneficiary_account_type) }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption text-grey">Agência</div>
                  <div class="text-body-1">{{ caseData?.beneficiary_agency }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption text-grey">Conta</div>
                  <div class="text-body-1">{{ caseData?.beneficiary_account }}</div>
                </v-col>
              </template>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- File Upload -->
        <v-file-input
          v-model="files"
          label="Comprovante de Transferência"
          prepend-icon="mdi-paperclip"
          accept="image/*,application/pdf"
          :rules="fileRules"
          :disabled="uploading"
          show-size
          chips
          multiple
          hint="Formatos: PDF, JPG, PNG (máx. 5MB cada)"
          persistent-hint
        >
          <template #selection="{ fileNames }">
            <v-chip
              v-for="fileName in fileNames"
              :key="fileName"
              size="small"
              label
              class="mr-2"
            >
              {{ fileName }}
            </v-chip>
          </template>
        </v-file-input>

        <!-- Error Alert -->
        <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn @click="close" :disabled="uploading">
          Cancelar
        </v-btn>
        <v-btn
          color="info"
          variant="flat"
          :loading="uploading"
          :disabled="!files || files.length === 0"
          @click="confirmTransfer"
        >
          Confirmar Transferência
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { api } from '@/services/api'

interface Props {
  modelValue: boolean
  caseData: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const files = ref<File[]>([])
const uploading = ref(false)
const error = ref('')

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Debug: Watch for dialog open
watch(() => props.modelValue, (newVal) => {
  console.log('TransferProofDialog modelValue changed:', newVal)
  if (newVal) {
    console.log('Dialog opened, caseData:', props.caseData)
  }
})

const fileRules = [
  (value: File[]) => {
    if (!value || value.length === 0) return 'Arquivo obrigatório'
    for (const file of value) {
      if (file.size > 5 * 1024 * 1024) {
        return `${file.name} excede 5MB`
      }
    }
    return true
  }
]

const formatCurrency = (value: any) => {
  if (!value) return '0,00'
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toFixed(2).replace('.', ',')
}

const formatAccountType = (type: string) => {
  const types: Record<string, string> = {
    'corrente': 'Conta Corrente',
    'poupanca': 'Conta Poupança',
    'pagamento': 'Conta Pagamento'
  }
  return types[type] || type
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    // Show success toast (you can add a toast component)
  } catch (err) {
    error.value = 'Erro ao copiar chave PIX'
  }
}

const confirmTransfer = async () => {
  if (!files.value || files.value.length === 0) return

  uploading.value = true
  error.value = ''

  try {
    console.log('Starting transfer confirmation...')
    console.log('Files to upload:', files.value)
    console.log('Case ID:', props.caseData.id)

    // 1. Upload attachments
    for (const file of files.value) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('case', props.caseData.id.toString())
      formData.append('attachment_type', 'payment_proof')

      console.log('Uploading file:', file.name)
      console.log('FormData entries:')
      for (const [key, value] of formData.entries()) {
        console.log(`  ${key}:`, value)
      }

      const uploadResult = await api.uploadAttachment(formData)
      console.log('Upload result:', uploadResult)

      if (uploadResult.error) {
        throw new Error(uploadResult.error)
      }

      if (!uploadResult.data || !uploadResult.data.id) {
        throw new Error('Upload não retornou ID do anexo')
      }

      console.log('✅ Attachment uploaded successfully, ID:', uploadResult.data.id)
    }

    // 2. Confirm transfer (changes status)
    console.log('Confirming transfer...')
    const confirmResult = await api.confirmTransfer(props.caseData.id)
    console.log('Confirm result:', confirmResult)

    if (confirmResult.error) {
      throw new Error(confirmResult.error)
    }

    emit('success')
    close()
  } catch (err: any) {
    console.error('Transfer confirmation error:', err)
    error.value = err.message || err.response?.data?.message || err.response?.data?.error || 'Erro ao confirmar transferência'
  } finally {
    uploading.value = false
  }
}

const close = () => {
  if (!uploading.value) {
    files.value = []
    error.value = ''
    isOpen.value = false
  }
}
</script>
