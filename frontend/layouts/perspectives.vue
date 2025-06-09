<template>
  <v-app>
    <the-header />
    <v-main>
      <v-container fluid>
        <v-row>
          <v-col cols="12">
            <nuxt />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import TheHeader from '~/components/layout/TheHeader'

export default {
  components: {
    TheHeader
  }
}
</script> 