<template>
  <v-card>
    <v-card-title>
      <v-row align="center">
        <v-col cols="12" md="6">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-hand-heart</v-icon>
            <span class="text-h6">{{ title }}</span>
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="d-flex align-center justify-md-end">
            <v-text-field
              v-model="search"
              density="compact"
              label="Buscar"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              hide-details
              single-line
              style="max-width: 240px;"
            />
          </div>
        </v-col>
      </v-row>
    </v-card-title>

    <v-card-text>
      <!-- Tabs for Staff -->
      <v-tabs v-if="isStaff" v-model="currentTab" color="primary" class="mb-4">
        <v-tab value="pending_approval">
          <v-icon start>mdi-clock-alert</v-icon>
          Pendentes de Aprovação
        </v-tab>
        <v-tab value="approved">
          <v-icon start>mdi-check-circle</v-icon>
          Aprovadas
        </v-tab>
        <v-tab value="rejected">
          <v-icon start>mdi-close-circle</v-icon>
          Rejeitadas
        </v-tab>
        <v-tab value="all">
          <v-icon start>mdi-view-list</v-icon>
          Todas
        </v-tab>
      </v-tabs>

      <!-- Data Table -->
      <v-data-table
        :headers="headers"
        :items="filteredDonations"
        :search="search"
        :loading="loading"
        item-value="id"
      >
        <!-- Recipient Column -->
        <template #item.recipient_name="{ item }">
          <div>
            <div class="font-weight-medium">{{ item.recipient_name }}</div>
            <div class="text-caption text-grey">
              Solicitado por: {{ item.requester_name }}
            </div>
          </div>
        </template>

        <!-- Amount Column -->
        <template #item.amount="{ item }">
          <span class="font-weight-bold text-success">
            R$ {{ Number(item.amount).toFixed(2) }}
          </span>
        </template>

        <!-- Urgency Column -->
        <template #item.urgency_level="{ item }">
          <v-chip
            :color="getUrgencyColor(item.urgency_level)"
            size="small"
            variant="flat"
          >
            {{ item.urgency_display }}
          </v-chip>
        </template>

        <!-- Status Column -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="flat"
          >
            {{ item.status_display }}
          </v-chip>
        </template>

        <!-- Created Date Column -->
        <template #item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <!-- Actions Column -->
        <template #item.actions="{ item }">
          <div class="d-flex ga-2">
            <!-- View Details -->
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="viewDetails(item)"
            />

            <!-- Member Actions (Edit/Delete) -->
            <template v-if="!isStaff">
              <v-btn
                v-if="item.can_edit"
                icon="mdi-pencil"
                size="small"
                variant="text"
                color="primary"
                @click="editDonation(item)"
              />
              <v-btn
                v-if="item.can_delete"
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="deleteDonation(item)"
              />
            </template>

            <!-- Admin Actions (Approve/Reject) -->
            <template v-if="isStaff && item.status === 'pending_approval'">
              <v-btn
                icon="mdi-check"
                size="small"
                variant="text"
                color="success"
                @click="approveDonation(item)"
              />
              <v-btn
                icon="mdi-close"
                size="small"
                variant="text"
                color="error"
                @click="openRejectDialog(item)"
              />
            </template>
          </div>
        </template>
      </v-data-table>
    </v-card-text>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedDonation">
        <v-card-title class="d-flex align-center">
          <span>Detalhes da Solicitação</span>
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="detailsDialog = false"
          />
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col cols="12">
              <div class="mb-4">
                <div class="text-caption text-grey mb-1">Beneficiário</div>
                <div class="text-h6">{{ selectedDonation.recipient_name }}</div>
              </div>

              <div class="mb-4">
                <div class="text-caption text-grey mb-1">Descrição do Beneficiário</div>
                <div>{{ selectedDonation.recipient_description }}</div>
              </div>

              <div class="mb-4">
                <div class="text-caption text-grey mb-1">Motivo da Necessidade</div>
                <div>{{ selectedDonation.reason }}</div>
              </div>

              <v-divider class="my-4" />

              <v-row>
                <v-col cols="6">
                  <div class="text-caption text-grey mb-1">Valor</div>
                  <div class="text-h6 text-success">R$ {{ Number(selectedDonation.amount).toFixed(2) }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption text-grey mb-1">Urgência</div>
                  <v-chip :color="getUrgencyColor(selectedDonation.urgency_level)" size="small">
                    {{ selectedDonation.urgency_display }}
                  </v-chip>
                </v-col>
              </v-row>

              <v-divider class="my-4" />

              <div class="mb-2">
                <div class="text-caption text-grey mb-1">Status</div>
                <v-chip :color="getStatusColor(selectedDonation.status)" size="small">
                  {{ selectedDonation.status_display }}
                </v-chip>
              </div>

              <div class="mb-2">
                <div class="text-caption text-grey mb-1">Solicitado por</div>
                <div>{{ selectedDonation.requester_name }}</div>
              </div>

              <div class="mb-2">
                <div class="text-caption text-grey mb-1">Data da Solicitação</div>
                <div>{{ formatDate(selectedDonation.created_at) }}</div>
              </div>

              <div v-if="selectedDonation.reviewed_by_name" class="mb-2">
                <div class="text-caption text-grey mb-1">Revisado por</div>
                <div>{{ selectedDonation.reviewed_by_name }}</div>
              </div>

              <div v-if="selectedDonation.approved_at" class="mb-2">
                <div class="text-caption text-grey mb-1">Data de Aprovação</div>
                <div>{{ formatDate(selectedDonation.approved_at) }}</div>
              </div>

              <div v-if="selectedDonation.rejection_reason" class="mb-2">
                <v-alert type="error" variant="tonal" density="compact">
                  <div class="text-caption text-grey mb-1">Motivo da Rejeição</div>
                  <div>{{ selectedDonation.rejection_reason }}</div>
                </v-alert>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Reject Dialog -->
    <v-dialog v-model="rejectDialog" max-width="500">
      <v-card>
        <v-card-title>Rejeitar Solicitação</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectionReason"
            label="Motivo da Rejeição"
            rows="4"
            variant="outlined"
            :rules="[v => !!v || 'Campo obrigatório']"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="rejectDialog = false">Cancelar</v-btn>
          <v-btn
            color="error"
            variant="flat"
            :disabled="!rejectionReason"
            :loading="loading"
            @click="confirmReject"
          >
            Rejeitar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { format } from 'date-fns'
import type { DonationRequest } from '@/services/api'
import { useConfirm } from '@/composables/useConfirm'

interface Props {
  donations: DonationRequest[]
  loading?: boolean
  title?: string
  isStaff?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  title: 'Solicitações de Doação',
  isStaff: false
})

const emit = defineEmits<{
  create: []
  edit: [donation: DonationRequest]
  delete: [donation: DonationRequest]
  approve: [donation: DonationRequest]
  reject: [donation: DonationRequest, reason: string]
  refresh: []
}>()

const { confirm } = useConfirm()

const search = ref('')
const currentTab = ref('pending_approval')
const detailsDialog = ref(false)
const rejectDialog = ref(false)
const selectedDonation = ref<DonationRequest | null>(null)
const rejectionReason = ref('')

const headers = computed(() => {
  const baseHeaders = [
    { title: 'Beneficiário', key: 'recipient_name', sortable: true },
    { title: 'Valor', key: 'amount', sortable: true },
    { title: 'Urgência', key: 'urgency_level', sortable: true },
    { title: 'Status', key: 'status', sortable: true },
    { title: 'Data', key: 'created_at', sortable: true },
    { title: 'Ações', key: 'actions', sortable: false, align: 'end' as const }
  ]
  return baseHeaders
})

const filteredDonations = computed(() => {
  if (!props.isStaff || currentTab.value === 'all') {
    return props.donations
  }
  return props.donations.filter(d => d.status === currentTab.value)
})

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending_approval': return 'orange'
    case 'approved': return 'green'
    case 'rejected': return 'red'
    default: return 'grey'
  }
}

const getUrgencyColor = (urgency: string) => {
  switch (urgency) {
    case 'critical': return 'red-darken-2'
    case 'high': return 'red'
    case 'medium': return 'orange'
    case 'low': return 'grey'
    default: return 'grey'
  }
}

const formatDate = (dateString: string) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm')
  } catch {
    return dateString
  }
}

const viewDetails = (donation: DonationRequest) => {
  selectedDonation.value = donation
  detailsDialog.value = true
}

const editDonation = (donation: DonationRequest) => {
  emit('edit', donation)
}

const deleteDonation = async (donation: DonationRequest) => {
  const confirmed = await confirm({
    title: 'Excluir Solicitação',
    message: `Tem certeza que deseja excluir a solicitação para "${donation.recipient_name}"?`,
    icon: 'mdi-delete-alert',
    variant: 'danger',
    confirmText: 'Excluir',
    cancelText: 'Cancelar'
  })

  if (confirmed) {
    emit('delete', donation)
  }
}

const approveDonation = async (donation: DonationRequest) => {
  const confirmed = await confirm({
    title: 'Aprovar Solicitação',
    message: `Deseja aprovar a solicitação de doação para "${donation.recipient_name}" no valor de R$ ${Number(donation.amount).toFixed(2)}?`,
    icon: 'mdi-check-circle',
    variant: 'success',
    confirmText: 'Aprovar',
    cancelText: 'Cancelar'
  })

  if (confirmed) {
    emit('approve', donation)
  }
}

const openRejectDialog = (donation: DonationRequest) => {
  selectedDonation.value = donation
  rejectionReason.value = ''
  rejectDialog.value = true
}

const confirmReject = () => {
  if (selectedDonation.value && rejectionReason.value) {
    emit('reject', selectedDonation.value, rejectionReason.value)
    rejectDialog.value = false
  }
}

// Reset tab when switching between staff/member view
watch(() => props.isStaff, () => {
  currentTab.value = 'pending_approval'
})
</script>
