<template>
  <v-app>
    <!-- Alerta de falha de ligação -->
    <v-alert
      v-if="$store.state.connectionError"
      type="error"
      prominent
      dense
      border="left"
      class="text-center"
    >
      ⚠️ Falha de ligação, por favor tente mais tarde!
    </v-alert>

    <the-header />

    <v-main>
      <nuxt />
    </v-main>

    <the-footer />
  </v-app>
</template>

<script>
import TheFooter from '@/components/layout/TheFooter'
import TheHeader from '@/components/layout/TheHeader'

export default {
  components: {
    TheFooter,
    TheHeader
  }
}
</script>
