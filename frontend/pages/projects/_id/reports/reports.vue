<template>
  <v-container class="mt-4 pt-16">
    <v-row justify="space-between" align="center" class="mb-4">
      <v-col cols="auto">
        <h2 class="text-h5 font-weight-bold">Estatística sobre Histórico de Anotações</h2>
      </v-col>
      <v-col cols="auto">
        <v-btn color="primary" @click="goToProjects">Voltar aos Projetos</v-btn>
      </v-col>
    </v-row>

    <v-card class="pa-4">
      <v-row>
        <v-col cols="12" sm="4">
          <v-select
            v-model="selectedUser"
            :items="userOptions"
            item-title="username"
            item-value="id"
            label="Filtrar por Utilizador"
            clearable
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model="startDate"
            label="Data Inicial"
            type="date"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model="endDate"
            label="Data Final"
            type="date"
          />
        </v-col>
      </v-row>

      <v-row class="mb-4">
        <v-col>
          <v-btn color="info" @click="fetchReport">Aplicar Filtros</v-btn>
          <v-btn class="ml-4" 
            color="secondary" @click="goToHistory">Ver Estatísticas Anteriores</v-btn>
          <v-btn class="ml-4" 
            color="info" @click="clearFilters">Limpar Filtros</v-btn>
        </v-col>
      </v-row>

      <v-simple-table>
        <thead>
          <tr>
            <th>Total de Anotações</th>
            <th>Total de Utilizadores</th>
            <th>Total de Regras</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ report.total_annotations }}</td>
            <td>{{ report.total_users }}</td>
            <td>{{ report.rules_count }}</td>
          </tr>
        </tbody>
      </v-simple-table>

      <v-row class="mt-4" align="center" justify="space-between">
        <v-col cols="auto">
          <v-btn color="success" @click="exportReport('csv')">Exportar CSV</v-btn>
          <v-btn class="ml-2" color="error" 
            @click="exportReport('pdf')">Exportar PDF</v-btn>
        </v-col>
        <v-col cols="auto">
          <v-btn text @click="goBack">← Voltar</v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script>
import axios from '@/services/api.service'

export default {
  data() {
    return {
      selectedUser: null,
      startDate: null,
      endDate: null,
      report: {
        total_annotations: 0,
        total_users: 0,
        rules_count: 0
      },
      userOptions: []
    }
  },
  methods: {
    async fetchReport() {
      try {
        const projectId = this.$route.params.id
        const params = {
          ...(this.selectedUser && { user_id: this.selectedUser }),
          ...(this.startDate && { start_date: this.startDate }),
          ...(this.endDate && { end_date: this.endDate })
        }

        const { data } = await axios.get(`/reports/historical-report/${projectId}/`, { params })
        this.report = data
      } catch (error) {
        console.error('Erro ao buscar relatório:', error)
      }
    },
    exportReport(format) {
      const projectId = this.$route.params.id
      const params = new URLSearchParams({
        ...(this.selectedUser && { user_id: this.selectedUser }),
        ...(this.startDate && { start_date: this.startDate }),
        ...(this.endDate && { end_date: this.endDate }),
        format
      }).toString()

      window.open(`/api/reports/historical-report/${projectId}/?${params}`, '_blank')
    },
    async loadUsers() {
      const projectId = this.$route.params.id
      const { data } = await axios.get(`/projects/${projectId}/members/`)
      this.userOptions = data
    },
    goToHistory() {
      const projectId = this.$route.params.id
      this.$router.replace(`/projects/${projectId}/reports/history`)
    },
    goToProjects() {
      this.$router.push('/projects')
    },
    goBack() {
      this.$router.back()
    },
    clearFilters() {
      this.selectedUser = null
      this.startDate = null
      this.endDate = null
      this.fetchReport()
    }
  },
  mounted() {
    this.loadUsers()
    this.fetchReport()
  }
}
</script>
