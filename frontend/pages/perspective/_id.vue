<template>
    <v-container>
      <v-card v-if="perspective">
        <v-card-title>{{ perspective.name }}</v-card-title>
        <v-card-text>
          <p>{{ perspective.description }}</p>
          <p>Criado em: {{ formatDate(perspective.created_at) }}</p>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script>
  export default {
    middleware: 'auth',
    data() {
      return {
        perspective: null,
        loading: false
      }
    },
    async mounted() {
      await this.loadPerspective()
    },
    methods: {
      async loadPerspective() {
        this.loading = true
        try {
          const response = await this.$axios.get(`/v1/api/perspective/${this.$route.params.id}/`)
          this.perspective = response.data
        } catch (error) {
          console.error('Erro ao carregar perspectiva:', error)
        } finally {
          this.loading = false
        }
      },
      formatDate(date) {
        return new Date(date).toLocaleString()
      }
    }
  }
  </script>