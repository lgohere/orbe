<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { useI18n } from 'vue-i18n'

const theme = useTheme()
const { locale } = useI18n()

onMounted(() => {
  // Initialize theme from localStorage or system preference
  initializeTheme()
  // Initialize language from localStorage or browser
  initializeLanguage()
})

function initializeTheme() {
  const savedTheme = localStorage.getItem('orbe-theme')

  if (savedTheme === 'orbe-black') {
    theme.global.name.value = 'orbe-black'
  } else {
    // White theme is default as per ORBE documentation
    theme.global.name.value = 'orbe-white'
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