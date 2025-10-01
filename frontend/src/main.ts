import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
// Google Fonts - Poppins
import '@fontsource/poppins/300.css' // Light
import '@fontsource/poppins/400.css' // Regular
import '@fontsource/poppins/500.css' // Medium
import '@fontsource/poppins/600.css' // SemiBold
import '@fontsource/poppins/700.css' // Bold
import { createVuetify } from 'vuetify'
import { VBtn, VApp, VMain, VContainer, VRow, VCol, VCard, VCardTitle, VCardText, VCardActions, VForm, VTextField, VSelect, VCheckbox, VProgressCircular, VStepper, VStepperItem, VStepperWindow, VStepperWindowItem, VStepperHeader, VDivider, VWindow, VWindowItem, VProgressLinear, VIcon, VAvatar, VAlert, VMenu, VList, VListItem, VListItemTitle } from 'vuetify/components'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

import App from './App.vue'
import router from './router'

// ORBE Global Styles
import './styles/main.css'

// Import locales
import ptBR from './locales/pt-BR.json'
import en from './locales/en.json'
import es from './locales/es.json'

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'pt-BR',
  fallbackLocale: 'pt-BR',
  messages: {
    'pt-BR': ptBR,
    en: en,
    es: es,
  },
})

// Create Vuetify instance with ORBE theme
const vuetify = createVuetify({
  components: {
    VBtn,
    VApp,
    VMain,
    VContainer,
    VRow,
    VCol,
    VCard,
    VCardTitle,
    VCardText,
    VCardActions,
    VForm,
    VTextField,
    VSelect,
    VCheckbox,
    VProgressCircular,
    VStepper,
    VStepperItem,
    VStepperWindow,
    VStepperWindowItem,
    VStepperHeader,
    VDivider,
    VWindow,
    VWindowItem,
    VProgressLinear,
    VIcon,
    VAvatar,
    VAlert,
    VMenu,
    VList,
    VListItem,
    VListItemTitle,
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'orbe-white',
    themes: {
      'orbe-white': {
        dark: false,
        colors: {
          primary: '#304E69',
          secondary: '#C79657',
          accent: '#C79657',
          background: '#DDEAF4',
          surface: '#FFFFFF',
          'surface-variant': '#F5F5F5',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
          'on-surface': '#304E69',
          'on-background': '#000000',
          'primary-darken-1': '#1F3A52',
          'secondary-darken-1': '#A67A43',
          success: '#4CAF50',
          info: '#2196F3',
          warning: '#FF9800',
          error: '#F44336',
        },
      },
      'orbe-black': {
        dark: true,
        colors: {
          // Core Brand Colors
          primary: '#7A9AB5',                // Lightened for better contrast on dark
          secondary: '#D4A96A',              // Lightened gold for visibility
          accent: '#D4A96A',

          // Surface Colors
          background: '#1A2733',             // Darker blue for better contrast
          surface: '#2A3F52',                // Mid-tone surface
          'surface-variant': '#344A5F',      // Lighter variant for elevation
          'surface-bright': '#3D5266',       // Brightest surface for cards

          // Text Colors (High Contrast for Dark Theme)
          'on-primary': '#FFFFFF',
          'on-secondary': '#1A1A1A',
          'on-surface': '#F5F5F5',           // Very light text for maximum contrast
          'on-background': '#FFFFFF',        // Pure white on dark background
          'on-surface-variant': '#E0E0E0',   // Slightly dimmed for secondary text

          // Semantic Text Colors
          'text-primary': '#FFFFFF',         // Main headings - pure white
          'text-secondary': '#E0E0E0',       // Body text - light grey
          'text-tertiary': '#B0B0B0',        // Captions - medium-light grey

          // State Colors
          'primary-darken-1': '#5B7A95',
          'secondary-darken-1': '#B8915A',
          success: '#66BB6A',
          info: '#42A5F5',
          warning: '#FFA726',
          error: '#EF5350',

          // Status Colors (for badges, chips)
          'success-lighten': '#81C784',
          'info-lighten': '#64B5F6',
          'warning-lighten': '#FFB74D',
          'error-lighten': '#E57373',
        },
      },
    },
  },
})

// Create app
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(vuetify)

app.mount('#app')