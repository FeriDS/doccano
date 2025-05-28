<template>
    <v-container>
      <v-row justify="space-between" align="center" class="mb-4">
        <v-col cols="auto">
          <v-card-title class="text-h5"></v-card-title>
        </v-col>
        <v-col cols="auto">
          <v-btn color="primary" @click="goBack"></v-btn>
        </v-col>
      </v-row>
  
      <v-card>
        <v-card-title>
            <v-row justify="space-between" align="center" class="w-100">
            <v-col cols="auto">
                <span class="text-h6">📚 Relatórios Gerados</span>
            </v-col>
            <v-col cols="auto">
                <v-btn text @click="goBack">← Voltar</v-btn>
            </v-col>
            </v-row>
        </v-card-title>

        <v-data-table
            :headers="headers"
            :items="reports"
            :items-per-page="5"
            class="elevation-1"
        >
            <template v-slot:item="{ item }">
            <tr>
                <td>{{ formatDate(item.created_at) }}</td>
                <td>{{ item.user_filter || 'Todos' }}</td>
                <td>{{ item.start_date || '-' }}</td>
                <td>{{ item.end_date || '-' }}</td>
                <td>{{ item.total_annotations }}</td>
                <td>{{ item.total_users }}</td>
                <td>{{ item.rules_count }}</td>
                <td>
                <v-btn icon @click="exportReport(item, 'csv')">
                    <v-icon>mdi-file-delimited</v-icon>
                </v-btn>
                <v-btn icon @click="exportReport(item, 'pdf')">
                    <v-icon>mdi-file-pdf</v-icon>
                </v-btn>
                </td>
            </tr>
            </template>
        </v-data-table>
        </v-card>

    </v-container>
  </template>
  
<script>
import axios from '@/services/api.service'

export default {
  data() {
    return {
      reports: [],
      headers: [
        { text: 'Data', value: 'created_at' },
        { text: 'Utilizador (filtro)', value: 'user_filter' },
        { text: 'Data Inicial', value: 'start_date' },
        { text: 'Data Final', value: 'end_date' },
        { text: 'Total Anotações', value: 'total_annotations' },
        { text: 'Total Utilizadores', value: 'total_users' },
        { text: 'Regras', value: 'rules_count' },
        { text: 'Ações', value: 'actions', sortable: false }
      ]
    }
  },

  mounted() {
    this.fetchReports()
  },

  methods: {
    async fetchReports() {
      try {
        const projectId = this.$route.params.id
        const { data } = await axios.get(`api/reports/reports_historicalreport/list/${projectId}/`)
        this.reports = data
      } catch (error) {
        console.error('Erro ao buscar relatórios:', error)
      }
    },

    exportReport(report, format) {
      const projectId = this.$route.params.id
      const params = new URLSearchParams({
        ...(report.user_filter && { user_id: report.user_filter }),
        ...(report.start_date && { start_date: report.start_date }),
        ...(report.end_date && { end_date: report.end_date }),
        format
      }).toString()

      window.open(`/api/reports/historical-report/${projectId}/?${params}`, '_blank')
    },

    formatDate(date) {
      return new Date(date).toLocaleString()
    },
    
    goBack() {
    this.$router.back()
    }
  }
}
</script>
