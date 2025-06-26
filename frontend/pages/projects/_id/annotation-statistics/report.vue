<template>
  <v-container class="mt-12">
    <v-card class="pa-8 text-center">
      <h1>Annotation Report View</h1>
      <div class="mt-4">Current path: <code>{{ $route.fullPath }}</code></div>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'AnnotationReportView'
}
</script>
