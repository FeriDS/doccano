<!-- <template>
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
          { text: 'Criado em', value: 'created_at' }
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
          const response = await this.$axios.get('/v1/api/perspective/?include_projects=true')
          this.perspectives = response.data
        } catch (error) {
          console.error('Erro ao carregar perspectivas:', error)
          this.$toast.error('Falha ao carregar perspectivas')
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
  </script> -->

  <template>
    <v-data-table
      :headers="headers"
      :items="perspectives"
      :loading="loading"
    >
      <template #[`item.projects`]="{ item }">
        <v-chip v-for="project in item.projects" :key="project.id" small class="mr-2">
          {{ project.name }}
        </v-chip>
      </template>
    </v-data-table>
  </template>
  
  <script>
  export default {
    data() {
      return {
        headers: [
          { text: 'Nome', value: 'name' },
          { text: 'Projetos', value: 'projects' },
          { text: 'Criado em', value: 'created_at' }
        ],
        perspectives: []
      }
    },
    async mounted() {
      await this.loadPerspectives()
    },
    methods: {
      async loadPerspectives() {
        try {
          const response = await this.$axios.get('/api/perspective/')
          this.perspectives = response.data.map(p => ({
            ...p,
            created_at: this.formatDate(p.created_at)
          }))
        } catch (error) {
          console.error('Erro ao carregar:', error)
        }
      },
      formatDate(date) {
        return new Date(date).toLocaleDateString()
      }
    }
  }
  </script>