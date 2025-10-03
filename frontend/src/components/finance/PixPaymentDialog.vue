<template>
  <v-dialog v-model="isOpen" max-width="500" persistent>
    <v-card rounded="lg">
      <!-- Header -->
      <v-card-title class="bg-primary text-white pa-6">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon icon="mdi-qrcode" class="mr-3" size="32" />
            <div>
              <div class="text-h5 font-weight-bold">Pagamento via PIX</div>
              <div class="text-caption text-white text-opacity-80">
                Mensalidade ORBE
              </div>
            </div>
          </div>
          <v-btn
            icon="mdi-close"
            variant="text"
            color="white"
            @click="close"
          />
        </div>
      </v-card-title>

      <v-card-text class="pa-6">
        <!-- Payment Amount -->
        <div class="text-center mb-6">
          <div class="text-caption text-medium-emphasis mb-1">
            Valor da Mensalidade
          </div>
          <div class="text-h3 font-weight-bold text-primary">
            R$ 60,00
          </div>
        </div>

        <v-divider class="mb-6" />

        <!-- QR Code -->
        <div class="text-center mb-6">
          <div class="mb-4">
            <img
              src="/qrcode-Orbe-Mensalidade-pix.png"
              alt="QR Code PIX"
              style="max-width: 280px; width: 100%; height: auto;"
              class="qr-code-image"
            />
          </div>
          <div class="text-body-2 text-medium-emphasis">
            Escaneie o QR Code com o app do seu banco
          </div>
        </div>

        <v-divider class="mb-4" />

        <!-- PIX Code Copy Section -->
        <div class="mb-4">
          <div class="text-body-2 font-weight-medium mb-2 text-center">
            Ou copie o código PIX:
          </div>

          <v-card
            variant="outlined"
            class="pix-code-card pa-4"
            @click="copyPixCode"
            style="cursor: pointer;"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="pix-code-text text-body-2 font-mono text-medium-emphasis flex-1 mr-3">
                {{ pixCode }}
              </div>
              <v-btn
                icon="mdi-content-copy"
                variant="tonal"
                color="primary"
                size="small"
                @click.stop="copyPixCode"
              />
            </div>
          </v-card>

          <div class="text-caption text-center text-medium-emphasis mt-2">
            Clique no código para copiar
          </div>
        </div>

        <!-- Instructions -->
        <v-alert
          type="info"
          variant="tonal"
          density="compact"
          class="mt-4"
        >
          <div class="text-body-2">
            <strong>Como pagar:</strong>
            <ol class="ml-4 mt-2">
              <li>Abra o app do seu banco</li>
              <li>Escolha a opção PIX</li>
              <li>Escaneie o QR Code ou cole o código</li>
              <li>Confirme o pagamento de R$ 60,00</li>
            </ol>
          </div>
        </v-alert>
      </v-card-text>

      <!-- Footer -->
      <v-card-actions class="pa-6 pt-0">
        <v-spacer />
        <v-btn
          color="grey-darken-1"
          variant="text"
          @click="close"
        >
          Fechar
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Success Toast -->
    <v-snackbar
      v-model="showCopiedToast"
      :timeout="3000"
      color="success"
      location="top"
    >
      <div class="d-flex align-center">
        <v-icon icon="mdi-check-circle" class="mr-2" />
        Código PIX copiado com sucesso!
      </div>
    </v-snackbar>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// PIX code from ORBE
const pixCode = '00020126360014BR.GOV.BCB.PIX011446005417000148520400005303986540560.005802BR5901N6001C62190515OrbeMensalidade63044975'

const isOpen = ref(props.modelValue)
const showCopiedToast = ref(false)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  isOpen.value = newValue
})

// Watch for internal changes
watch(isOpen, (newValue) => {
  emit('update:modelValue', newValue)
})

function close() {
  isOpen.value = false
}

async function copyPixCode() {
  try {
    await navigator.clipboard.writeText(pixCode)
    showCopiedToast.value = true
  } catch (error) {
    console.error('Failed to copy PIX code:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = pixCode
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      showCopiedToast.value = true
    } catch (err) {
      console.error('Fallback copy failed:', err)
    }
    document.body.removeChild(textArea)
  }
}
</script>

<style scoped>
.qr-code-image {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.qr-code-image:hover {
  transform: scale(1.02);
}

.pix-code-card {
  transition: all 0.2s ease;
}

.pix-code-card:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
  border-color: rgb(var(--v-theme-primary));
}

.pix-code-text {
  word-break: break-all;
  line-height: 1.4;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.font-mono {
  font-family: 'Courier New', Courier, monospace;
}

ol {
  padding-left: 1rem;
}

ol li {
  margin-bottom: 0.25rem;
}
</style>
