<template>
  <div class="step-container">
    <v-card-text class="pa-8 text-center">
      <!-- Success Animation -->
      <div class="success-animation mb-6">
        <v-avatar size="80" color="success" class="mb-4 success-pulse">
          <v-icon size="40" color="white">mdi-check</v-icon>
        </v-avatar>
      </div>

      <!-- Success Message -->
      <h3 class="orbe-title text-h4 text-primary mb-4">
        {{ $t('onboarding.completed.title') }}
      </h3>

      <p class="orbe-body text-h6 text-medium-emphasis mb-3">
        {{ $t('onboarding.completed.subtitle') }}
      </p>

      <p class="orbe-body text-body-1 text-medium-emphasis mb-8">
        {{ $t('onboarding.completed.message') }}
      </p>

      <!-- Loading indicator -->
      <div class="d-flex align-center justify-center mb-6">
        <v-progress-circular
          indeterminate
          color="secondary"
          size="24"
          width="3"
          class="me-3"
        />
        <span class="orbe-body text-body-2 text-medium-emphasis">
          {{ $t('common.redirecting') }}
        </span>
      </div>

      <!-- Manual redirect button (fallback) -->
      <v-btn
        to="/dashboard"
        color="secondary"
        size="large"
        rounded="pill"
        prepend-icon="mdi-view-dashboard"
        class="font-weight-bold"
        min-width="200"
      >
        {{ $t('onboarding.completed.goToDashboard') }}
      </v-btn>
    </v-card-text>
  </div>
</template>

<script setup lang="ts">
// No script logic needed for completion step
</script>

<style scoped>
.step-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-animation {
  position: relative;
}

.success-pulse {
  animation: successPulse 2s ease-in-out infinite;
}

@keyframes successPulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 20px rgba(76, 175, 80, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0);
  }
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .pa-8 {
    padding: 2rem !important;
  }

  .text-h4 {
    font-size: 1.5rem !important;
  }

  .text-h6 {
    font-size: 1.1rem !important;
  }

  .success-pulse {
    width: 60px !important;
    height: 60px !important;
  }
}
</style>