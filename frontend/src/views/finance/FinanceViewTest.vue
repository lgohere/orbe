<template>
  <v-container>
    <h1>Finance Test - Minimal Version</h1>
    <p>If you see this, the route works!</p>

    <v-card class="mt-4">
      <v-card-title>Test Card</v-card-title>
      <v-card-text>
        <p>User: {{ authStore.user?.email }}</p>
        <p>Role: {{ authStore.user?.role }}</p>
        <p>Is Staff: {{ isStaff }}</p>
      </v-card-text>
    </v-card>

    <!-- Test Component Imports -->
    <v-card class="mt-4">
      <v-card-title>Testing MembershipFeesTable...</v-card-title>
      <v-card-text>
        <MembershipFeesTable
          :membership-fees="[]"
          :is-staff="isStaff"
          @refresh="() => {}"
        />
      </v-card-text>
    </v-card>

    <v-card class="mt-4">
      <v-card-title>Testing DonationsTable...</v-card-title>
      <v-card-text>
        <DonationsTable
          :donations="[]"
          :is-staff="isStaff"
          @refresh="() => {}"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import MembershipFeesTable from '@/components/finance/MembershipFeesTable.vue'
import DonationsTable from '@/components/finance/DonationsTable.vue'

const authStore = useAuthStore()

const isStaff = computed(() => {
  const role = authStore.user?.role
  return role === 'SUPER_ADMIN' || role === 'BOARD' || role === 'FISCAL_COUNCIL'
})
</script>
