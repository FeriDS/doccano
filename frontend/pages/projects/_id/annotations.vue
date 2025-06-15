<template>
  <v-container class="mt-16">
    <v-row>
      <v-col cols="12" class="mb-8">
        <v-toolbar flat color="transparent">
          <v-toolbar-title class="headline font-weight-bold">
            Side to Side Annotation with Discrepancies
          </v-toolbar-title>
        </v-toolbar>
      </v-col>
      <v-col cols="6">
        <v-card v-if="annotation">
          <v-card-title>Anotação Selecionada (1)</v-card-title>
          <v-card-text>
            <div><strong>Texto:</strong> {{ annotation.text }}</div>
            <!-- Adicione outros campos relevantes aqui -->
          </v-card-text>
        </v-card>
        <v-alert v-else type="info" outlined>
          Nenhuma anotação selecionada.
        </v-alert>
      </v-col>
      <v-col cols="6">
        <v-card v-if="annotation">
          <v-card-title>Anotação Selecionada (2)</v-card-title>
          <v-card-text>
            <div><strong>Texto:</strong> {{ annotation.text }}</div>
            <!-- Adicione outros campos relevantes aqui -->
          </v-card-text>
        </v-card>
        <v-alert v-else type="info" outlined>
          Nenhuma anotação selecionada.
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  data() {
    return {
      annotation: null as any
    }
  },
  async created() {
    const projectId = this.$route.query.id
    const exampleId = this.$route.query.example
    if (projectId && exampleId) {
      this.annotation = await this.$services.example.get(projectId, exampleId)
    }
  }
})
</script>

<style scoped>
.annotation-page {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
</style>