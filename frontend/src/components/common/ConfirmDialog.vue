<template>
  <v-dialog
    v-model="isOpen"
    :max-width="maxWidth"
    :persistent="persistent"
    @click:outside="handleCancel"
  >
    <v-card :class="['confirm-dialog', variant]">
      <!-- Header -->
      <v-card-title class="d-flex align-center pa-6">
        <v-icon
          v-if="icon"
          :icon="icon"
          :color="iconColor"
          size="28"
          class="mr-3"
        />
        <span class="text-h6 font-weight-bold">{{ title }}</span>
      </v-card-title>

      <v-divider />

      <!-- Content -->
      <v-card-text class="pa-6">
        <div v-if="$slots.default" class="text-body-1">
          <slot />
        </div>
        <p v-else class="text-body-1 mb-0">{{ message }}</p>

        <!-- Input field (optional) -->
        <v-text-field
          v-if="requireInput"
          v-model="inputValue"
          :label="inputLabel"
          :placeholder="inputPlaceholder"
          :rules="inputRules"
          variant="outlined"
          density="comfortable"
          class="mt-4"
          autofocus
        />
      </v-card-text>

      <v-divider />

      <!-- Actions -->
      <v-card-actions class="pa-4">
        <v-spacer />

        <v-btn
          :text="cancelText"
          :variant="cancelVariant"
          :color="cancelColor"
          :disabled="loading"
          @click="handleCancel"
        />

        <v-btn
          :text="confirmText"
          :variant="confirmVariant"
          :color="confirmColor"
          :loading="loading"
          :disabled="!canConfirm"
          @click="handleConfirm"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

export interface ConfirmDialogProps {
  modelValue: boolean
  title: string
  message?: string
  icon?: string
  variant?: 'default' | 'warning' | 'danger' | 'success' | 'info'
  maxWidth?: string | number
  persistent?: boolean
  loading?: boolean

  // Texts
  confirmText?: string
  cancelText?: string

  // Button variants
  confirmVariant?: 'flat' | 'text' | 'elevated' | 'tonal' | 'outlined' | 'plain'
  cancelVariant?: 'flat' | 'text' | 'elevated' | 'tonal' | 'outlined' | 'plain'

  // Input (optional)
  requireInput?: boolean
  inputLabel?: string
  inputPlaceholder?: string
  inputValidation?: string // e.g., "CONFIRMAR" para validar ação crítica
}

const props = withDefaults(defineProps<ConfirmDialogProps>(), {
  message: '',
  variant: 'default',
  maxWidth: 500,
  persistent: false,
  loading: false,
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  confirmVariant: 'flat',
  cancelVariant: 'text',
  requireInput: false,
  inputLabel: '',
  inputPlaceholder: '',
  inputValidation: ''
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'confirm': []
  'cancel': []
}>()

// Internal state
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const inputValue = ref('')

// Reset input when dialog opens
watch(isOpen, (newVal) => {
  if (newVal) {
    inputValue.value = ''
  }
})

// Computed properties
const iconColor = computed(() => {
  switch (props.variant) {
    case 'warning':
      return 'warning'
    case 'danger':
      return 'error'
    case 'success':
      return 'success'
    case 'info':
      return 'info'
    default:
      return 'primary'
  }
})

const confirmColor = computed(() => {
  switch (props.variant) {
    case 'warning':
      return 'warning'
    case 'danger':
      return 'error'
    case 'success':
      return 'success'
    case 'info':
      return 'info'
    default:
      return 'primary'
  }
})

const cancelColor = computed(() => {
  return 'grey-darken-1'
})

const inputRules = computed(() => {
  if (!props.requireInput) return []

  const rules = [(v: string) => !!v || 'Campo obrigatório']

  if (props.inputValidation) {
    rules.push((v: string) => v === props.inputValidation || `Digite "${props.inputValidation}" para confirmar`)
  }

  return rules
})

const canConfirm = computed(() => {
  if (!props.requireInput) return true

  if (props.inputValidation) {
    return inputValue.value === props.inputValidation
  }

  return !!inputValue.value
})

// Methods
const handleConfirm = () => {
  if (!canConfirm.value) return
  emit('confirm')
}

const handleCancel = () => {
  if (props.persistent || props.loading) return
  emit('cancel')
  isOpen.value = false
}
</script>

<style scoped>
.confirm-dialog {
  border-radius: 12px !important;
  overflow: hidden;
}

.confirm-dialog.warning {
  border-top: 4px solid rgb(var(--v-theme-warning));
}

.confirm-dialog.danger {
  border-top: 4px solid rgb(var(--v-theme-error));
}

.confirm-dialog.success {
  border-top: 4px solid rgb(var(--v-theme-success));
}

.confirm-dialog.info {
  border-top: 4px solid rgb(var(--v-theme-info));
}

.confirm-dialog :deep(.v-card-title) {
  line-height: 1.4;
  word-break: break-word;
}

.confirm-dialog :deep(.v-card-text) {
  color: rgb(var(--v-theme-on-surface)) !important;
  line-height: 1.6;
}
</style>
