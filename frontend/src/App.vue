<template>
  <v-app>
    <router-view />

    <!-- Global Confirm Dialog -->
    <ConfirmDialog
      v-model="confirmState.isOpen"
      :title="confirmState.title"
      :message="confirmState.message"
      :icon="confirmState.icon"
      :variant="confirmState.variant"
      :confirm-text="confirmState.confirmText"
      :cancel-text="confirmState.cancelText"
      :require-input="confirmState.requireInput"
      :input-label="confirmState.inputLabel"
      :input-placeholder="confirmState.inputPlaceholder"
      :input-validation="confirmState.inputValidation"
      :persistent="confirmState.persistent"
      :loading="confirmState.loading"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </v-app>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { useI18n } from 'vue-i18n'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { useConfirm } from '@/composables/useConfirm'

const theme = useTheme()
const { locale } = useI18n()
const { state: confirmState, handleConfirm, handleCancel } = useConfirm()

onMounted(() => {
  // Initialize theme from localStorage or system preference
  initializeTheme()
  // Initialize language from localStorage or browser
  initializeLanguage()
})

function initializeTheme() {
  const savedTheme = localStorage.getItem('orbe-theme')

  if (savedTheme === 'orbe-black') {
    theme.change('orbe-black')
  } else {
    // White theme is default as per ORBE documentation
    theme.change('orbe-white')
  }
}

function initializeLanguage() {
  const savedLanguage = localStorage.getItem('orbe-language')
  const browserLanguage = navigator.language.toLowerCase()

  let language = 'pt-BR' // default

  if (savedLanguage && ['pt-BR', 'en', 'es'].includes(savedLanguage)) {
    language = savedLanguage
  } else if (browserLanguage.startsWith('en')) {
    language = 'en'
  } else if (browserLanguage.startsWith('es')) {
    language = 'es'
  }

  locale.value = language
  localStorage.setItem('orbe-language', language)
}
</script>