<template>
  <div class="page-content">
    <v-container>
      <v-card>
        <v-card-title class="headline">
          Lista de Perspectivas
          <v-spacer></v-spacer>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Pesquisar"
            single-line
            hide-details
          ></v-text-field>
        </v-card-title>

      <v-data-table
        :headers="headers"
        :items="perspectives"
        :search="search"
        :loading="loading"
        @click:row="viewPerspective"
      >
        <template #[`item.created_at`]="{ item }">
          {{ formatDate(item.created_at) }}
        </template>
      </v-data-table>
    </v-card>
  </v-container>
  </div>
</template>

<script>
export default {
  middleware: 'auth',
  data() {
    return {
      search: '',
      loading: false,
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Nome', value: 'name' },
        { text: 'Descrição', value: 'description' },
        { text: 'Criado em', value: 'created_at' },
        { text: 'Projetos', value: 'projects' }
      ],
      perspectives: []
    }
  },
  async mounted() {
    await this.loadPerspectives()
  },
  methods: {
    async loadPerspectives() {
      this.loading = true
      try {
        const response = await this.$axios.get('/v1/api/perspective/')
        this.perspectives = response.data
      } catch (error) {
        console.error('Erro ao carregar perspectivas:', error)
      } finally {
        this.loading = false
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleString()
    },
    viewPerspective(item) {
      this.$router.push(`/perspective/${item.id}`)
    }
  }
}
</script>

<style scoped>
.page-content {
  margin-top: 80px; /* Ajuste conforme necessário */
  padding: 20px;
}
</style>