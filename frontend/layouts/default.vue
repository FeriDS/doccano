<template>
  <v-app>
    <v-snackbar
      v-model="showTechIssue"
      :timeout="0"
      top
      color="error"
    >
      We're sorry, but there was a technical issue with the server. Please try again later.
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="showTechIssue = false">
          Understood
        </v-btn>
      </template>
    </v-snackbar>
    <the-header />
    <nuxt />
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
  },
  data() {
    return {
      showTechIssue: false
    }
  },
  mounted() {
    const params = new URLSearchParams(window.location.search)
    if (params.get('error') === 'techissue') {
      this.showTechIssue = true
    }
  }
}
</script>
