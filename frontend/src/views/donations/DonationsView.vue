<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">{{ $t('donations.title') }}</h1>
        <p class="text-subtitle-1 text-medium-emphasis mb-6">
          {{ $t('donations.subtitle') }}
        </p>
      </v-col>
    </v-row>

    <!-- Action Cards -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card
          class="donation-action-card"
          hover
          @click="showVoluntaryDonationDialog = true"
        >
          <v-card-title class="text-h5">
            <v-icon icon="mdi-heart" color="primary" class="mr-2" />
            {{ $t('donations.makeVoluntaryDonation') }}
          </v-card-title>
          <v-card-text>
            <p class="text-body-1">
              {{ $t('donations.voluntaryDonationDescription') }}
            </p>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" variant="flat">
              {{ $t('donations.donateCta') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card
          class="donation-action-card"
          hover
          @click="showRequestDonationDialog = true"
        >
          <v-card-title class="text-h5">
            <v-icon icon="mdi-hand-heart" color="secondary" class="mr-2" />
            {{ $t('donations.requestDonation') }}
          </v-card-title>
          <v-card-text>
            <p class="text-body-1">
              {{ $t('donations.requestDonationDescription') }}
            </p>
          </v-card-text>
          <v-card-actions>
            <v-btn color="secondary" variant="flat">
              {{ $t('donations.requestCta') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- My Donation Requests -->
    <v-row class="mt-8">
      <v-col cols="12">
        <h2 class="text-h5 mb-4">{{ $t('donations.myRequests') }}</h2>

        <v-alert v-if="loading" type="info" variant="tonal">
          {{ $t('common.loading') }}
        </v-alert>

        <v-alert v-else-if="error" type="error" variant="tonal" class="mb-4">
          {{ error }}
        </v-alert>

        <div v-else-if="donationRequests.length === 0">
          <v-alert type="info" variant="tonal">
            {{ $t('donations.noRequests') }}
          </v-alert>
        </div>

        <v-row v-else>
          <v-col
            v-for="request in donationRequests"
            :key="request.id"
            cols="12"
            md="6"
            lg="4"
          >
            <DonationRequestCard
              :request="request"
              @edit="editRequest"
              @delete="deleteRequest"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <!-- Dialogs -->
    <VoluntaryDonationDialog
      v-model="showVoluntaryDonationDialog"
      @success="onVoluntaryDonationSuccess"
    />

    <RequestDonationDialog
      v-model="showRequestDonationDialog"
      :edit-request="editingRequest"
      @success="onRequestDonationSuccess"
      @close="editingRequest = null"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiService, type DonationRequest } from '@/services/api'
import DonationRequestCard from '@/components/donations/DonationRequestCard.vue'
import VoluntaryDonationDialog from '@/components/donations/VoluntaryDonationDialog.vue'
import RequestDonationDialog from '@/components/donations/RequestDonationDialog.vue'

const showVoluntaryDonationDialog = ref(false)
const showRequestDonationDialog = ref(false)
const donationRequests = ref<DonationRequest[]>([])
const editingRequest = ref<DonationRequest | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const loadDonationRequests = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await apiService.getMyDonationRequests()
    if (response.error) {
      error.value = response.error
    } else {
      donationRequests.value = response.data || []
    }
  } catch (err) {
    error.value = 'Failed to load donation requests'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const onVoluntaryDonationSuccess = () => {
  showVoluntaryDonationDialog.value = false
  // TODO: Show success message
}

const onRequestDonationSuccess = () => {
  showRequestDonationDialog.value = false
  editingRequest.value = null
  loadDonationRequests()
  // TODO: Show success message
}

const editRequest = (request: DonationRequest) => {
  editingRequest.value = request
  showRequestDonationDialog.value = true
}

const deleteRequest = async (request: DonationRequest) => {
  if (!confirm('Are you sure you want to delete this request?')) {
    return
  }

  try {
    const response = await apiService.deleteDonationRequest(request.id)
    if (response.error) {
      error.value = response.error
    } else {
      loadDonationRequests()
    }
  } catch (err) {
    error.value = 'Failed to delete request'
    console.error(err)
  }
}

onMounted(() => {
  loadDonationRequests()
})
</script>

<style scoped>
.donation-action-card {
  cursor: pointer;
  transition: transform 0.2s;
  height: 100%;
}

.donation-action-card:hover {
  transform: translateY(-4px);
}
</style>
