<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold text-primary mb-2">Meu Perfil</h1>
        <p class="text-body-1 text-grey-darken-1">
          Gerencie suas informações pessoais e preferências
        </p>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p class="text-body-1 text-grey mt-4">Carregando perfil...</p>
    </div>

    <!-- Error Alert -->
    <v-alert v-if="error" type="error" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <!-- Success Snackbar -->
    <v-snackbar v-model="showSuccess" color="success" timeout="3000">
      {{ successMessage }}
    </v-snackbar>

    <!-- Profile Content -->
    <v-row v-if="!loading">
      <!-- Personal Information Card -->
      <v-col cols="12" md="8">
        <v-card class="mb-4">
          <v-card-title class="text-h6 bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-account</v-icon>
            Informações Pessoais
          </v-card-title>
          <v-card-text class="pa-4">
            <v-form ref="personalFormRef" v-model="personalFormValid">
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="personalData.first_name"
                    label="Nome"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || 'Nome é obrigatório']"
                    required
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="personalData.last_name"
                    label="Sobrenome"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || 'Sobrenome é obrigatório']"
                    required
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="personalData.email"
                    label="Email"
                    type="email"
                    variant="outlined"
                    density="comfortable"
                    readonly
                    hint="Email não pode ser alterado"
                    persistent-hint
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="profileData.phone"
                    label="Telefone"
                    variant="outlined"
                    density="comfortable"
                    placeholder="+55 13 99999-9999"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="personalData.role_display"
                    label="Função"
                    variant="outlined"
                    density="comfortable"
                    readonly
                    hint="Definida pelo administrador"
                    persistent-hint
                  />
                </v-col>
              </v-row>

              <v-divider class="my-4" />

              <v-btn
                color="primary"
                size="large"
                prepend-icon="mdi-content-save"
                :loading="savingPersonal"
                :disabled="!personalFormValid"
                @click="savePersonalInfo"
              >
                Salvar Informações Pessoais
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Location Information Card -->
        <v-card class="mb-4">
          <v-card-title class="text-h6 bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-map-marker</v-icon>
            Localidade
          </v-card-title>
          <v-card-text class="pa-4">
            <v-form ref="addressFormRef" v-model="addressFormValid">
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="profileData.country"
                    label="País"
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
                <v-col cols="12" sm="8">
                  <v-text-field
                    v-model="profileData.city"
                    label="Cidade"
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
                <v-col cols="12" sm="4">
                  <v-text-field
                    v-model="profileData.state"
                    label="Estado"
                    variant="outlined"
                    density="comfortable"
                    placeholder="SP"
                  />
                </v-col>
              </v-row>

              <v-divider class="my-4" />

              <v-btn
                color="primary"
                size="large"
                prepend-icon="mdi-content-save"
                :loading="savingAddress"
                :disabled="!addressFormValid"
                @click="saveAddress"
              >
                Salvar Localidade
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Change Password Card -->
        <v-card>
          <v-card-title class="text-h6 bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-lock</v-icon>
            Alterar Senha
          </v-card-title>
          <v-card-text class="pa-4">
            <v-form ref="passwordFormRef" v-model="passwordFormValid">
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="passwordData.current_password"
                    label="Senha Atual"
                    type="password"
                    variant="outlined"
                    density="comfortable"
                    :rules="[v => !!v || 'Senha atual é obrigatória']"
                    required
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="passwordData.new_password"
                    label="Nova Senha"
                    type="password"
                    variant="outlined"
                    density="comfortable"
                    :rules="[
                      v => !!v || 'Nova senha é obrigatória',
                      v => v.length >= 8 || 'Senha deve ter pelo menos 8 caracteres'
                    ]"
                    required
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="passwordData.confirm_password"
                    label="Confirmar Nova Senha"
                    type="password"
                    variant="outlined"
                    density="comfortable"
                    :rules="[
                      v => !!v || 'Confirmação é obrigatória',
                      v => v === passwordData.new_password || 'Senhas não coincidem'
                    ]"
                    required
                  />
                </v-col>
              </v-row>

              <v-divider class="my-4" />

              <v-btn
                color="warning"
                size="large"
                prepend-icon="mdi-key"
                :loading="savingPassword"
                :disabled="!passwordFormValid"
                @click="changePassword"
              >
                Alterar Senha
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Sidebar -->
      <v-col cols="12" md="4">
        <!-- Profile Summary Card -->
        <v-card class="mb-4">
          <v-card-title class="text-h6 bg-primary text-white">
            <v-icon class="mr-2">mdi-account-circle</v-icon>
            Resumo do Perfil
          </v-card-title>
          <v-card-text class="pa-4">
            <div class="text-center mb-4">
              <v-avatar color="primary" size="100">
                <span class="text-h3 text-white">
                  {{ userInitials }}
                </span>
              </v-avatar>
            </div>

            <v-list>
              <v-list-item>
                <template #prepend>
                  <v-icon>mdi-email</v-icon>
                </template>
                <v-list-item-title class="text-caption">Email</v-list-item-title>
                <v-list-item-subtitle class="text-body-2">
                  {{ personalData.email }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider />

              <v-list-item>
                <template #prepend>
                  <v-icon>mdi-badge-account</v-icon>
                </template>
                <v-list-item-title class="text-caption">Função</v-list-item-title>
                <v-list-item-subtitle class="text-body-2">
                  {{ personalData.role_display }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider />

              <v-list-item>
                <template #prepend>
                  <v-icon>mdi-calendar</v-icon>
                </template>
                <v-list-item-title class="text-caption">Membro desde</v-list-item-title>
                <v-list-item-subtitle class="text-body-2">
                  {{ formatDate(personalData.date_joined) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Preferences Card -->
        <v-card class="mb-4">
          <v-card-title class="text-h6 bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-cog</v-icon>
            Preferências
          </v-card-title>
          <v-card-text class="pa-4">
            <v-form ref="preferencesFormRef" v-model="preferencesFormValid">
              <v-select
                v-model="profileData.theme_preference"
                :items="themeOptions"
                label="Tema"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-palette"
                class="mb-4"
              />

              <v-select
                v-model="profileData.language_preference"
                :items="languageOptions"
                label="Idioma"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-translate"
                class="mb-4"
              />

              <v-text-field
                v-model.number="profileData.membership_due_day"
                label="Dia de Vencimento da Mensalidade"
                type="number"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-calendar-month"
                :rules="[
                  v => v >= 1 && v <= 28 || 'Deve estar entre 1 e 28'
                ]"
                hint="Dia do mês (1-28)"
                persistent-hint
              />

              <v-divider class="my-4" />

              <v-btn
                color="primary"
                size="large"
                prepend-icon="mdi-content-save"
                block
                :loading="savingPreferences"
                :disabled="!preferencesFormValid"
                @click="savePreferences"
              >
                Salvar Preferências
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Account Info Card -->
        <v-card>
          <v-card-title class="text-h6 bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-information</v-icon>
            Informações da Conta
          </v-card-title>
          <v-card-text class="pa-4">
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title class="text-caption">ID do Usuário</v-list-item-title>
                <v-list-item-subtitle class="text-body-2">
                  {{ personalData.id }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="text-caption">Método de Registro</v-list-item-title>
                <v-list-item-subtitle class="text-body-2">
                  <v-chip size="x-small" :color="registrationMethodColor">
                    {{ registrationMethodLabel }}
                  </v-chip>
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="text-caption">Status da Conta</v-list-item-title>
                <v-list-item-subtitle class="text-body-2">
                  <v-chip size="x-small" color="success">Ativa</v-chip>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// State
const loading = ref(false)
const error = ref('')
const showSuccess = ref(false)
const successMessage = ref('')

const personalFormRef = ref()
const addressFormRef = ref()
const passwordFormRef = ref()
const preferencesFormRef = ref()

const personalFormValid = ref(false)
const addressFormValid = ref(false)
const passwordFormValid = ref(false)
const preferencesFormValid = ref(false)

const savingPersonal = ref(false)
const savingAddress = ref(false)
const savingPassword = ref(false)
const savingPreferences = ref(false)

interface PersonalData {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string
  role_display: string
  registration_method: string
  date_joined: string
}

interface ProfileData {
  phone: string
  address_line1: string
  address_line2: string
  city: string
  state: string
  zip_code: string
  country: string
  theme_preference: string
  language_preference: string
  membership_due_day: number
}

const personalData = ref<PersonalData>({
  id: 0,
  email: '',
  first_name: '',
  last_name: '',
  role: '',
  role_display: '',
  registration_method: '',
  date_joined: ''
})

const profileData = ref<ProfileData>({
  phone: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  zip_code: '',
  country: 'Brasil',
  theme_preference: 'white',
  language_preference: 'pt-BR',
  membership_due_day: 5
})

const passwordData = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// Options
const themeOptions = [
  { title: 'Tema Claro', value: 'white' },
  { title: 'Tema Escuro', value: 'black' }
]

const languageOptions = [
  { title: 'Português (Brasil)', value: 'pt-BR' },
  { title: 'English', value: 'en' },
  { title: 'Español', value: 'es' }
]

// Computed
const userInitials = computed(() => {
  const first = personalData.value.first_name?.charAt(0) || ''
  const last = personalData.value.last_name?.charAt(0) || ''
  return (first + last).toUpperCase()
})

const registrationMethodLabel = computed(() => {
  return personalData.value.registration_method === 'manual'
    ? 'Manual (Staff)'
    : 'Convidado'
})

const registrationMethodColor = computed(() => {
  return personalData.value.registration_method === 'manual'
    ? 'primary'
    : 'info'
})

// Methods
async function loadProfile() {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch('/api/users/me/', {
      headers: {
        'Authorization': `Token ${authStore.token}`
      }
    })

    if (!response.ok) throw new Error('Failed to load profile')

    const data = await response.json()

    personalData.value = {
      id: data.id,
      email: data.email,
      first_name: data.first_name,
      last_name: data.last_name,
      role: data.role,
      role_display: getRoleDisplay(data.role),
      registration_method: data.registration_method,
      date_joined: data.date_joined
    }

    if (data.profile) {
      profileData.value = {
        phone: data.profile.phone || '',
        address_line1: data.profile.address_line1 || '',
        address_line2: data.profile.address_line2 || '',
        city: data.profile.city || '',
        state: data.profile.state || '',
        zip_code: data.profile.zip_code || '',
        country: data.profile.country || 'Brasil',
        theme_preference: data.profile.theme_preference || 'white',
        language_preference: data.profile.language_preference || 'pt-BR',
        membership_due_day: data.profile.membership_due_day || 5
      }
    }
  } catch (err) {
    console.error('Error loading profile:', err)
    error.value = 'Erro ao carregar perfil'
  } finally {
    loading.value = false
  }
}

async function savePersonalInfo() {
  savingPersonal.value = true
  error.value = ''

  try {
    // Update user first name and last name
    const userResponse = await fetch('/api/users/me/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        first_name: personalData.value.first_name,
        last_name: personalData.value.last_name
      })
    })

    if (!userResponse.ok) throw new Error('Failed to update personal info')

    // Update phone in profile
    const phoneResponse = await fetch('/api/users/preferences/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone: profileData.value.phone
      })
    })

    if (!phoneResponse.ok) throw new Error('Failed to update phone')

    successMessage.value = 'Informações pessoais atualizadas com sucesso!'
    showSuccess.value = true

    // Update auth store
    await authStore.initialize()
  } catch (err) {
    console.error('Error saving personal info:', err)
    error.value = 'Erro ao salvar informações pessoais'
  } finally {
    savingPersonal.value = false
  }
}

async function saveAddress() {
  savingAddress.value = true
  error.value = ''

  try {
    const response = await fetch('/api/users/preferences/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone: profileData.value.phone,
        city: profileData.value.city,
        state: profileData.value.state,
        country: profileData.value.country
      })
    })

    if (!response.ok) throw new Error('Failed to update location')

    successMessage.value = 'Localidade atualizada com sucesso!'
    showSuccess.value = true
  } catch (err) {
    console.error('Error saving address:', err)
    error.value = 'Erro ao salvar endereço'
  } finally {
    savingAddress.value = false
  }
}

async function savePreferences() {
  savingPreferences.value = true
  error.value = ''

  try {
    const response = await fetch('/api/users/preferences/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        theme_preference: profileData.value.theme_preference,
        language_preference: profileData.value.language_preference,
        membership_due_day: profileData.value.membership_due_day
      })
    })

    if (!response.ok) throw new Error('Failed to update preferences')

    successMessage.value = 'Preferências atualizadas com sucesso!'
    showSuccess.value = true

    // Apply theme change
    // TODO: Implement theme switching in main.ts
  } catch (err) {
    console.error('Error saving preferences:', err)
    error.value = 'Erro ao salvar preferências'
  } finally {
    savingPreferences.value = false
  }
}

async function changePassword() {
  savingPassword.value = true
  error.value = ''

  try {
    const response = await fetch('/api/auth/password/change/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        old_password: passwordData.value.current_password,
        new_password1: passwordData.value.new_password,
        new_password2: passwordData.value.confirm_password
      })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.old_password?.[0] || data.new_password1?.[0] || 'Erro ao alterar senha')
    }

    successMessage.value = 'Senha alterada com sucesso!'
    showSuccess.value = true

    // Clear form
    passwordData.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
    passwordFormRef.value?.reset()
  } catch (err: any) {
    console.error('Error changing password:', err)
    error.value = err.message || 'Erro ao alterar senha'
  } finally {
    savingPassword.value = false
  }
}

function getRoleDisplay(role: string): string {
  const roleLabels: Record<string, string> = {
    'SUPER_ADMIN': 'Super Administrador',
    'BOARD': 'Conselho Diretor',
    'FISCAL_COUNCIL': 'Conselho Fiscal',
    'MEMBER': 'Membro'
  }
  return roleLabels[role] || role
}

function formatDate(dateString: string): string {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(date)
}

// Lifecycle
onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.v-list-item {
  padding-left: 0;
  padding-right: 0;
}
</style>
