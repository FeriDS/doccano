<template>
  <v-app>
    <TheHeader />
    <v-main>
      <v-container fluid>
        <Nuxt />
      </v-container>
    </v-main>
    <TheFooter /> <!-- Se tiver footer -->
  </v-app>
</template>

<script>
import TheHeader from '@/components/layout/TheHeader.vue'

export default {
  components: { TheHeader }
}
</script>

<style scoped>
.v-main {
  padding-top: 64px !important; /* Altura do header */
}
</style>