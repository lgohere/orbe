<template>
  <v-dialog v-model="isOpen" max-width="700" persistent>
    <v-card v-if="props.caseData">
      <v-card-title class="d-flex align-center bg-purple">
        <v-icon class="mr-2" color="white">mdi-camera</v-icon>
        <span class="text-white">Enviar Comprovantes</span>
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" color="white" @click="close" :disabled="uploading" />
      </v-card-title>

      <v-card-text class="pt-6">
        <v-alert type="info" variant="tonal" class="mb-4">
          <div class="text-body-2">
            <strong>Instruções:</strong>
            <ul class="mt-2 ml-4">
              <li>Comprove que utilizou a doação conforme solicitado</li>
              <li>Envie fotos claras e legíveis dos comprovantes</li>
              <li>Exemplos: notas fiscais, recibos, fotos dos itens comprados</li>
              <li>Formatos aceitos: JPG, PNG, PDF (máx. 5MB cada)</li>
              <li><strong>Mínimo: 1 arquivo | Máximo: 5 arquivos</strong></li>
            </ul>
          </div>
        </v-alert>

        <!-- Case Info Reminder -->
        <v-card variant="outlined" class="mb-4">
          <v-card-text>
            <div class="text-caption text-grey mb-1">Caso</div>
            <div class="text-h6 font-weight-bold mb-2">{{ caseData?.title }}</div>

            <div class="text-caption text-grey mb-1">Descrição Pública</div>
            <div class="text-body-2">{{ caseData?.public_description }}</div>

            <div class="mt-3">
              <v-chip color="success" size="small">
                <v-icon start size="small">mdi-cash</v-icon>
                R$ {{ formatCurrency(caseData?.total_value) }}
              </v-chip>
            </div>
          </v-card-text>
        </v-card>

        <!-- File Upload -->
        <v-file-input
          v-model="files"
          label="Comprovantes (Fotos ou PDFs)"
          prepend-icon="mdi-image-multiple"
          accept="image/*,application/pdf"
          :rules="fileRules"
          :disabled="uploading"
          show-size
          chips
          multiple
          counter
          hint="Envie de 1 a 5 comprovantes (fotos ou PDFs, máx. 5MB cada)"
          persistent-hint
        >
          <template #selection="{ fileNames }">
            <template v-for="(fileName, index) in fileNames" :key="fileName">
              <v-chip
                size="small"
                label
                class="mr-2 mb-2"
                closable
                @click:close="removeFile(index)"
              >
                <v-icon start size="small">mdi-file-image</v-icon>
                {{ fileName }}
              </v-chip>
            </template>
          </template>
        </v-file-input>

        <!-- Preview Images -->
        <div v-if="imagePreviews.length > 0" class="mt-4">
          <div class="text-caption text-grey mb-2">Pré-visualização:</div>
          <v-row dense>
            <v-col
              v-for="(preview, index) in imagePreviews"
              :key="index"
              cols="4"
            >
              <v-img
                :src="preview"
                aspect-ratio="1"
                cover
                class="rounded"
                style="border: 2px solid #e0e0e0"
              />
            </v-col>
          </v-row>
        </div>

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
          color="purple"
          variant="flat"
          :loading="uploading"
          :disabled="!files || files.length === 0"
          @click="submitProof"
        >
          <v-icon start>mdi-send</v-icon>
          Enviar Comprovantes
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
const imagePreviews = ref<string[]>([])
const uploading = ref(false)
const error = ref('')

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const fileRules = [
  (value: File[]) => {
    if (!value || value.length === 0) return 'Pelo menos 1 arquivo é obrigatório'
    if (value.length > 5) return 'Máximo de 5 arquivos permitidos'
    for (const file of value) {
      if (file.size > 5 * 1024 * 1024) {
        return `${file.name} excede 5MB`
      }
    }
    return true
  }
]

// Watch files for preview
watch(files, (newFiles) => {
  imagePreviews.value = []

  if (newFiles && newFiles.length > 0) {
    newFiles.forEach((file) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          if (e.target?.result) {
            imagePreviews.value.push(e.target.result as string)
          }
        }
        reader.readAsDataURL(file)
      }
    })
  }
})

const removeFile = (index: number) => {
  if (files.value) {
    files.value = files.value.filter((_, i) => i !== index)
  }
}

const submitProof = async () => {
  if (!files.value || files.value.length === 0) return

  uploading.value = true
  error.value = ''

  try {
    console.log('Starting member proof submission...')
    console.log('Files to upload:', files.value.length)
    console.log('Case ID:', props.caseData.id)

    // 1. Upload all attachments
    for (const file of files.value) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('case', props.caseData.id.toString())
      formData.append('attachment_type', 'photo_evidence')

      console.log('Uploading file:', file.name)
      const uploadResult = await api.uploadAttachment(formData)

      if (uploadResult.error) {
        throw new Error(uploadResult.error)
      }

      if (!uploadResult.data || !uploadResult.data.id) {
        throw new Error('Upload não retornou ID do anexo')
      }

      console.log('✅ Attachment uploaded successfully, ID:', uploadResult.data.id)
    }

    // 2. Submit member proof (changes status)
    console.log('Submitting member proof...')
    const submitResult = await api.submitMemberProof(props.caseData.id)
    console.log('Submit result:', submitResult)

    if (submitResult.error) {
      throw new Error(submitResult.error)
    }

    emit('success')
    close()
  } catch (err: any) {
    console.error('Member proof submission error:', err)
    error.value = err.message || err.response?.data?.message || err.response?.data?.error || 'Erro ao enviar comprovantes'
  } finally {
    uploading.value = false
  }
}

const formatCurrency = (value: any): string => {
  if (!value) return '0,00'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return numValue.toFixed(2).replace('.', ',')
}

const close = () => {
  if (!uploading.value) {
    files.value = []
    imagePreviews.value = []
    error.value = ''
    isOpen.value = false
  }
}
</script>
