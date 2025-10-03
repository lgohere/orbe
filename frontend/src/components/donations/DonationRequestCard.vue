<template>
  <v-card class="donation-request-card" elevation="2">
    <v-card-title class="d-flex align-center">
      <span class="text-h6">{{ request.recipient_name }}</span>
      <v-spacer />
      <v-chip
        :color="statusColor"
        size="small"
        variant="flat"
      >
        {{ request.status_display }}
      </v-chip>
    </v-card-title>

    <v-card-subtitle class="mt-2">
      <div class="d-flex align-center">
        <v-chip
          :color="urgencyColor"
          size="small"
          variant="tonal"
          class="mr-2"
        >
          {{ request.urgency_display }}
        </v-chip>
        <span class="text-h6 font-weight-bold" style="color: var(--v-primary-base);">
          R$ {{ request.amount.toFixed(2) }}
        </span>
      </div>
    </v-card-subtitle>

    <v-card-text>
      <p class="text-body-2 mb-2">
        <strong>{{ $t('donations.reason') }}:</strong> {{ request.reason }}
      </p>
      <p class="text-caption text-medium-emphasis">
        {{ $t('donations.requestedOn') }}: {{ formatDate(request.created_at) }}
      </p>

      <div v-if="request.status === 'rejected' && request.rejection_reason" class="mt-3">
        <v-alert type="error" density="compact" variant="tonal">
          <strong>{{ $t('donations.rejectionReason') }}:</strong> {{ request.rejection_reason }}
        </v-alert>
      </div>

      <div v-if="request.status === 'approved'" class="mt-3">
        <v-alert type="success" density="compact" variant="tonal">
          {{ $t('donations.approvedMessage') }}
        </v-alert>
      </div>
    </v-card-text>

    <v-card-actions v-if="request.can_edit || request.can_delete">
      <v-btn
        v-if="request.can_edit"
        color="primary"
        variant="text"
        size="small"
        prepend-icon="mdi-pencil"
        @click="$emit('edit', request)"
      >
        {{ $t('common.edit') }}
      </v-btn>
      <v-btn
        v-if="request.can_delete"
        color="error"
        variant="text"
        size="small"
        prepend-icon="mdi-delete"
        @click="$emit('delete', request)"
      >
        {{ $t('common.delete') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DonationRequest } from '@/services/api'
import { format } from 'date-fns'

const props = defineProps<{
  request: DonationRequest
}>()

defineEmits<{
  edit: [request: DonationRequest]
  delete: [request: DonationRequest]
}>()

const statusColor = computed(() => {
  switch (props.request.status) {
    case 'pending_approval':
      return 'orange'
    case 'approved':
      return 'green'
    case 'rejected':
      return 'red'
    default:
      return 'grey'
  }
})

const urgencyColor = computed(() => {
  switch (props.request.urgency_level) {
    case 'critical':
      return 'red-darken-2'
    case 'high':
      return 'red'
    case 'medium':
      return 'orange'
    case 'low':
      return 'grey'
    default:
      return 'grey'
  }
})

const formatDate = (dateString: string) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy')
  } catch {
    return dateString
  }
}
</script>

<style scoped>
.donation-request-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
