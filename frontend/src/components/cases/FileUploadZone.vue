<template>
  <div class="file-upload-zone">
    <!-- Upload Area -->
    <div
      v-if="!disabled"
      class="upload-dropzone"
      :class="{ 'dragover': isDragging, 'disabled': disabled }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @click="triggerFileInput"
    >
      <input
        ref="fileInputRef"
        type="file"
        multiple
        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        style="display: none"
        @change="handleFileSelect"
      />

      <div class="upload-content text-center">
        <v-icon size="64" :color="isDragging ? 'primary' : 'grey-lighten-1'">
          mdi-cloud-upload-outline
        </v-icon>
        <h3 class="text-h6 mt-3 mb-2">
          {{ isDragging ? 'Solte os arquivos aqui' : 'Arraste arquivos ou clique para selecionar' }}
        </h3>
        <p class="text-body-2 text-grey">
          PDF, JPG, PNG, DOC, DOCX (máx. 5MB cada)
        </p>
      </div>
    </div>

    <!-- Disabled Message -->
    <v-alert v-if="disabled && !caseId" type="info" density="compact" class="mb-4">
      <template #prepend>
        <v-icon>mdi-information</v-icon>
      </template>
      Salve o caso como rascunho antes de adicionar anexos
    </v-alert>

    <!-- Upload Progress -->
    <v-alert v-if="uploading" type="info" density="compact" class="mb-4">
      <div class="d-flex align-center">
        <v-progress-circular indeterminate size="20" width="2" class="mr-3" />
        <span>Enviando arquivos... {{ uploadProgress }}%</span>
      </div>
    </v-alert>

    <!-- Error Alert -->
    <v-alert v-if="error" type="error" density="compact" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <!-- Files List -->
    <v-list v-if="modelValue.length > 0" class="mt-4">
      <v-list-subheader class="text-subtitle-2 font-weight-bold">
        Arquivos Anexados ({{ modelValue.length }})
      </v-list-subheader>

      <v-list-item
        v-for="file in modelValue"
        :key="file.id"
        class="border rounded mb-2"
      >
        <template #prepend>
          <v-avatar :color="file.is_image ? 'primary-lighten-4' : 'grey-lighten-3'" size="48">
            <v-icon :color="file.is_image ? 'primary' : 'grey-darken-1'">
              {{ getFileIcon(file) }}
            </v-icon>
          </v-avatar>
        </template>

        <v-list-item-title class="font-weight-medium">
          {{ file.file_name }}
        </v-list-item-title>

        <v-list-item-subtitle>
          <v-chip size="x-small" class="mr-2">{{ file.file_type }}</v-chip>
          {{ formatFileSize(file.file_size) }}
          <span v-if="file.uploaded_at" class="text-grey">
            • Enviado em {{ formatDate(file.uploaded_at) }}
          </span>
        </v-list-item-subtitle>

        <template #append>
          <div class="d-flex align-center gap-2">
            <!-- Preview/Download Button -->
            <v-btn
              v-if="file.file_url"
              icon="mdi-download"
              variant="text"
              size="small"
              :href="file.file_url"
              target="_blank"
              download
            />

            <!-- Delete Button -->
            <v-btn
              v-if="canDelete"
              icon="mdi-delete"
              variant="text"
              size="small"
              color="error"
              @click="confirmDelete(file)"
            />
          </div>
        </template>
      </v-list-item>
    </v-list>

    <!-- Empty State -->
    <v-alert v-if="modelValue.length === 0 && !disabled" type="info" density="compact" class="mt-4">
      <template #prepend>
        <v-icon>mdi-information</v-icon>
      </template>
      Nenhum arquivo anexado. Adicione documentos comprobatórios para fortalecer o caso.
    </v-alert>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon class="mr-2" color="error">mdi-delete-alert</v-icon>
          Confirmar Exclusão
        </v-card-title>
        <v-card-text>
          <p class="text-body-1">
            Tem certeza que deseja remover o arquivo <strong>{{ fileToDelete?.file_name }}</strong>?
          </p>
          <p class="text-body-2 text-grey mt-2">
            Esta ação não pode ser desfeita.
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showDeleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" @click="deleteFile" :loading="deleting">Excluir</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

interface FileAttachment {
  id?: number
  file?: File
  file_name: string
  file_type: string
  file_size: number
  file_url?: string
  uploaded_at?: string
  is_image?: boolean
  file_icon?: string
}

interface Props {
  modelValue: FileAttachment[]
  caseId?: number | null
  disabled?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: FileAttachment[]): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  caseId: null
})

const emit = defineEmits<Emits>()

const authStore = useAuthStore()

// State
const fileInputRef = ref<HTMLInputElement>()
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const deleting = ref(false)
const error = ref('')
const showDeleteDialog = ref(false)
const fileToDelete = ref<FileAttachment | null>(null)

// Constants
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ALLOWED_TYPES = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
const ALLOWED_MIMES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

// Computed
const canDelete = computed(() => {
  // Can delete if case is draft or rejected (editable)
  return !props.disabled
})

// Methods
function triggerFileInput() {
  if (props.disabled) return
  fileInputRef.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files

  if (!files || files.length === 0) return

  processFiles(Array.from(files))

  // Reset input
  target.value = ''
}

function handleDrop(event: DragEvent) {
  isDragging.value = false

  if (props.disabled) return

  const files = event.dataTransfer?.files

  if (!files || files.length === 0) return

  processFiles(Array.from(files))
}

async function processFiles(files: File[]) {
  error.value = ''

  // Validate files
  const validFiles: File[] = []

  for (const file of files) {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      error.value = `Arquivo "${file.name}" excede o tamanho máximo de 5MB`
      continue
    }

    // Check file type
    const extension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!ALLOWED_TYPES.includes(extension)) {
      error.value = `Tipo de arquivo "${extension}" não permitido. Use: ${ALLOWED_TYPES.join(', ')}`
      continue
    }

    validFiles.push(file)
  }

  if (validFiles.length === 0) return

  // If no case ID, just show files locally (will upload after case creation)
  if (!props.caseId) {
    const localFiles: FileAttachment[] = validFiles.map(file => ({
      file,
      file_name: file.name,
      file_type: file.name.split('.').pop()?.toUpperCase() || 'FILE',
      file_size: file.size,
      is_image: file.type.startsWith('image/')
    }))

    emit('update:modelValue', [...props.modelValue, ...localFiles])
    return
  }

  // Upload files to backend
  await uploadFiles(validFiles)
}

async function uploadFiles(files: File[]) {
  uploading.value = true
  uploadProgress.value = 0

  try {
    const totalFiles = files.length
    let uploadedCount = 0

    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('case', props.caseId!.toString())

      const response = await fetch('/api/assistance/attachments/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${authStore.token}`
        },
        body: formData
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(extractErrorMessage(data))
      }

      const attachment = await response.json()

      // Add to list
      emit('update:modelValue', [...props.modelValue, attachment])

      uploadedCount++
      uploadProgress.value = Math.round((uploadedCount / totalFiles) * 100)
    }
  } catch (err: any) {
    console.error('Error uploading files:', err)
    error.value = err.message || 'Erro ao enviar arquivos'
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

function confirmDelete(file: FileAttachment) {
  fileToDelete.value = file
  showDeleteDialog.value = true
}

async function deleteFile() {
  if (!fileToDelete.value) return

  // If file doesn't have ID, just remove from local list
  if (!fileToDelete.value.id) {
    const filtered = props.modelValue.filter(f => f !== fileToDelete.value)
    emit('update:modelValue', filtered)
    showDeleteDialog.value = false
    fileToDelete.value = null
    return
  }

  deleting.value = true
  error.value = ''

  try {
    const response = await fetch(`/api/assistance/attachments/${fileToDelete.value.id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(extractErrorMessage(data))
    }

    // Remove from list
    const filtered = props.modelValue.filter(f => f.id !== fileToDelete.value!.id)
    emit('update:modelValue', filtered)

    showDeleteDialog.value = false
    fileToDelete.value = null
  } catch (err: any) {
    console.error('Error deleting file:', err)
    error.value = err.message || 'Erro ao excluir arquivo'
  } finally {
    deleting.value = false
  }
}

function getFileIcon(file: FileAttachment): string {
  if (file.file_icon) return file.file_icon

  const type = file.file_type?.toLowerCase() || ''

  if (type === 'pdf') return 'mdi-file-pdf-box'
  if (['jpg', 'jpeg', 'png', 'gif'].includes(type)) return 'mdi-file-image'
  if (['doc', 'docx'].includes(type)) return 'mdi-file-word'

  return 'mdi-file-document'
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function extractErrorMessage(errorData: any): string {
  if (typeof errorData === 'string') return errorData

  const errors = []
  for (const key in errorData) {
    if (Array.isArray(errorData[key])) {
      errors.push(...errorData[key])
    } else {
      errors.push(errorData[key])
    }
  }

  return errors.length > 0 ? errors[0] : 'Erro ao processar requisição'
}
</script>

<style scoped>
.file-upload-zone {
  width: 100%;
}

.upload-dropzone {
  border: 2px dashed rgb(var(--v-theme-grey-lighten-1));
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: rgb(var(--v-theme-grey-lighten-5));
}

.upload-dropzone:hover:not(.disabled) {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.upload-dropzone.dragover {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.1);
  transform: scale(1.02);
}

.upload-dropzone.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-content {
  pointer-events: none;
}

.v-list-item {
  transition: all 0.2s ease;
}

.v-list-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.gap-2 {
  gap: 8px;
}
</style>
