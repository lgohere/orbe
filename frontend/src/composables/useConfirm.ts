import { ref } from 'vue'

export interface ConfirmOptions {
  title: string
  message?: string
  icon?: string
  variant?: 'default' | 'warning' | 'danger' | 'success' | 'info'
  confirmText?: string
  cancelText?: string
  requireInput?: boolean
  inputLabel?: string
  inputPlaceholder?: string
  inputValidation?: string
  persistent?: boolean
}

interface ConfirmState extends ConfirmOptions {
  isOpen: boolean
  loading: boolean
  resolve: ((value: boolean) => void) | null
}

const state = ref<ConfirmState>({
  isOpen: false,
  loading: false,
  title: '',
  message: '',
  icon: undefined,
  variant: 'default',
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  requireInput: false,
  inputLabel: '',
  inputPlaceholder: '',
  inputValidation: '',
  persistent: false,
  resolve: null
})

export function useConfirm() {
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      state.value = {
        ...state.value,
        ...options,
        isOpen: true,
        loading: false,
        resolve
      }
    })
  }

  const handleConfirm = () => {
    if (state.value.resolve) {
      state.value.resolve(true)
    }
    close()
  }

  const handleCancel = () => {
    if (state.value.resolve) {
      state.value.resolve(false)
    }
    close()
  }

  const setLoading = (loading: boolean) => {
    state.value.loading = loading
  }

  const close = () => {
    state.value.isOpen = false
    state.value.loading = false
  }

  return {
    state,
    confirm,
    handleConfirm,
    handleCancel,
    setLoading,
    close
  }
}
