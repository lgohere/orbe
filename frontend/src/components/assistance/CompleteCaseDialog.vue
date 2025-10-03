<template>
  <v-dialog v-model="isOpen" max-width="800" persistent scrollable>
    <v-card v-if="props.caseData">
      <v-card-title class="d-flex align-center bg-success">
        <v-icon class="mr-2" color="white">mdi-check-all</v-icon>
        <span class="text-white">Validar e Concluir Caso</span>
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" color="white" @click="close" :disabled="loading" />
      </v-card-title>

      <v-card-text class="pt-6">
        <v-alert type="warning" variant="tonal" class="mb-4">
          <div class="text-body-2">
            <strong>Atenção!</strong> Antes de concluir, verifique:
            <ul class="mt-2 ml-4">
              <li>✅ Comprovante de transferência está correto</li>
              <li>✅ Comprovantes do membro comprovam o uso correto da doação</li>
              <li>✅ Todos os documentos estão legíveis e válidos</li>
              <li>✅ O valor aplicado corresponde ao valor doado</li>
            </ul>
          </div>
        </v-alert>

        <!-- Case Summary -->
        <v-card variant="outlined" class="mb-4">
          <v-card-title class="bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-file-document</v-icon>
            Resumo do Caso
          </v-card-title>
          <v-card-text>
            <v-row dense>
              <v-col cols="12">
                <div class="text-caption text-grey">Título</div>
                <div class="text-h6 font-weight-bold">{{ caseData?.title }}</div>
              </v-col>
              <v-col cols="12">
                <div class="text-caption text-grey">Descrição Pública</div>
                <div class="text-body-2">{{ caseData?.public_description }}</div>
              </v-col>
              <v-col cols="6">
                <div class="text-caption text-grey">Valor Total</div>
                <div class="text-h6 text-success">R$ {{ formatCurrency(caseData?.total_value) }}</div>
              </v-col>
              <v-col cols="6">
                <div class="text-caption text-grey">Beneficiário</div>
                <div class="text-body-1">{{ caseData?.beneficiary_name }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Attachments Review -->
        <v-card variant="outlined">
          <v-card-title class="bg-grey-lighten-4">
            <v-icon class="mr-2">mdi-paperclip</v-icon>
            Anexos para Validação ({{ attachmentsSummary.total }})
          </v-card-title>
          <v-card-text>
            <!-- Transfer Proofs -->
            <div class="mb-4">
              <div class="text-subtitle-2 font-weight-bold mb-2">
                <v-icon size="small" class="mr-1">mdi-bank-transfer</v-icon>
                Comprovantes de Transferência ({{ attachmentsSummary.transferProofs }})
              </div>

              <v-alert
                v-if="attachmentsSummary.transferProofs === 0"
                type="error"
                variant="tonal"
                density="compact"
              >
                ⚠️ Nenhum comprovante de transferência encontrado!
              </v-alert>

              <v-row v-else dense>
                <v-col
                  v-for="attachment in transferProofs"
                  :key="attachment.id"
                  cols="12" sm="6"
                >
                  <v-card variant="outlined">
                    <v-list-item :href="attachment.file_url" target="_blank">
                      <template #prepend>
                        <v-avatar color="info-lighten-4">
                          <v-icon :icon="attachment.is_image ? 'mdi-file-image' : 'mdi-file-pdf-box'" color="info" />
                        </v-avatar>
                      </template>
                      <v-list-item-title class="text-body-2">{{ attachment.file_name }}</v-list-item-title>
                      <v-list-item-subtitle class="text-caption">
                        {{ attachment.file_type }} • {{ attachment.file_size_mb }} MB
                      </v-list-item-subtitle>
                      <template #append>
                        <v-icon>mdi-open-in-new</v-icon>
                      </template>
                    </v-list-item>
                  </v-card>
                </v-col>
              </v-row>
            </div>

            <v-divider class="my-4" />

            <!-- Member Proofs -->
            <div>
              <div class="text-subtitle-2 font-weight-bold mb-2">
                <v-icon size="small" class="mr-1">mdi-camera</v-icon>
                Comprovantes do Membro ({{ attachmentsSummary.memberProofs }})
              </div>

              <v-alert
                v-if="attachmentsSummary.memberProofs === 0"
                type="error"
                variant="tonal"
                density="compact"
              >
                ⚠️ Nenhum comprovante do membro encontrado!
              </v-alert>

              <v-row v-else dense>
                <v-col
                  v-for="attachment in memberProofs"
                  :key="attachment.id"
                  cols="12" sm="6" md="4"
                >
                  <v-card variant="outlined" class="h-100">
                    <v-img
                      v-if="attachment.is_image"
                      :src="attachment.file_url"
                      aspect-ratio="1"
                      cover
                      class="cursor-pointer"
                      @click="openImage(attachment.file_url)"
                    >
                      <template #placeholder>
                        <div class="d-flex align-center justify-center fill-height">
                          <v-progress-circular indeterminate color="grey-lighten-1" />
                        </div>
                      </template>
                    </v-img>

                    <v-card-text v-else class="text-center py-8">
                      <v-icon size="64" color="grey-lighten-2">mdi-file-pdf-box</v-icon>
                      <div class="text-caption mt-2">{{ attachment.file_name }}</div>
                    </v-card-text>

                    <v-card-actions>
                      <v-btn
                        :href="attachment.file_url"
                        target="_blank"
                        variant="text"
                        size="small"
                        block
                      >
                        <v-icon start size="small">mdi-open-in-new</v-icon>
                        Abrir
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

        <!-- Error Alert -->
        <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn @click="close" :disabled="loading">
          Cancelar
        </v-btn>
        <v-btn
          color="success"
          variant="flat"
          :loading="loading"
          :disabled="!canComplete"
          @click="completeCase"
        >
          <v-icon start>mdi-check-all</v-icon>
          Validar e Concluir
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Image Viewer Dialog -->
    <v-dialog v-model="imageViewerOpen" max-width="90vw">
      <v-card>
        <v-card-title class="d-flex align-center">
          <span>Visualização</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="imageViewerOpen = false" />
        </v-card-title>
        <v-card-text class="pa-0">
          <v-img :src="selectedImage" contain max-height="80vh" />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
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

const loading = ref(false)
const error = ref('')
const imageViewerOpen = ref(false)
const selectedImage = ref('')

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const transferProofs = computed(() => {
  return props.caseData?.attachments?.filter((a: any) => a.attachment_type === 'payment_proof') || []
})

const memberProofs = computed(() => {
  return props.caseData?.attachments?.filter((a: any) => a.attachment_type === 'photo_evidence') || []
})

const attachmentsSummary = computed(() => {
  return {
    total: props.caseData?.attachments?.length || 0,
    transferProofs: transferProofs.value.length,
    memberProofs: memberProofs.value.length
  }
})

const canComplete = computed(() => {
  return attachmentsSummary.value.transferProofs > 0 && attachmentsSummary.value.memberProofs > 0
})

const openImage = (url: string) => {
  selectedImage.value = url
  imageViewerOpen.value = true
}

const formatCurrency = (value: any): string => {
  if (!value) return '0,00'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return numValue.toFixed(2).replace('.', ',')
}

const completeCase = async () => {
  if (!canComplete.value) {
    error.value = 'Caso não pode ser concluído: faltam comprovantes'
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('Completing case:', props.caseData.id)
    const result = await api.completeCase(props.caseData.id)
    console.log('Complete result:', result)

    if (result.error) {
      throw new Error(result.error)
    }

    emit('success')
    close()
  } catch (err: any) {
    console.error('Complete case error:', err)
    error.value = err.message || err.response?.data?.message || err.response?.data?.error || 'Erro ao concluir caso'
  } finally {
    loading.value = false
  }
}

const close = () => {
  if (!loading.value) {
    error.value = ''
    isOpen.value = false
  }
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
</style>
