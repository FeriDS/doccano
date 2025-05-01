<template>
  <v-container class="pa-6">
    <v-card class="pa-4">
      <v-card-title>
        <v-row no-gutters style="width: 100%;">
          <v-col class="d-flex flex-column align-start">
            <span class="text-h6">Relatórios de Anotações</span>
            <v-btn small color="primary" class="mt-2" @click="generateReport">
              Gerar novo relatório
            </v-btn>
          </v-col>
          <v-col cols="auto" class="d-flex justify-end">
            <v-btn text color="primary" class="ml-auto" @click="$router.back()">
              ← Voltar
            </v-btn>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text>
        <v-select
          v-if="reports.length"
          v-model="selectedReportId"
          :items="reports"
          item-value="id"
          item-text="created_at"
          label="Selecionar relatório"
          dense
          outlined
        />

        <div v-if="selectedReportId">
          <v-row>
            <v-col cols="12" md="4">
              <v-select
                v-model="filters.annotator"
                :items="annotators"
                item-value="user"
                item-text="user"
                label="Filtrar por utilizador"
                dense
                outlined
                clearable
              />
            </v-col>

            <v-col cols="12" md="4">
              <v-menu
                ref="startMenu"
                v-model="startMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="filters.start"
                    label="Data de início"
                    readonly
                    dense
                    outlined
                    v-bind="attrs"
                    v-on="on"
                  />
                </template>
                <v-date-picker v-model="filters.start" @input="startMenu = false" />
              </v-menu>
            </v-col>

            <v-col cols="12" md="4">
              <v-menu
                ref="endMenu"
                v-model="endMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="filters.end"
                    label="Data de fim"
                    readonly
                    dense
                    outlined
                    v-bind="attrs"
                    v-on="on"
                  />
                </template>
                <v-date-picker v-model="filters.end" @input="endMenu = false" />
              </v-menu>
            </v-col>
          </v-row>

          <v-btn
            color="success"
            class="mb-4"
            :disabled="filteredResults.length === 0"
            @click="exportCSV"
          >
            Exportar CSV
          </v-btn>

          <v-data-table
            :headers="headers"
            :items="filteredResults"
            :items-per-page="10"
          />
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
export default {
  layout: 'default',
  data() {
    return {
      reports: [],
      selectedReportId: null,
      reportData: [],
      error: null,
      projectName: '',
      filters: {
        annotator: null,
        start: null,
        end: null
      },
      startMenu: false,
      endMenu: false,
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Texto', value: 'text' },
        { text: 'Anotador', value: 'user' },
        { text: 'Data', value: 'created_at' },
        { text: 'Projeto', value: 'project' },
        { text: 'Perspetiva', value: 'perspective' }
      ]
    }
  },
  computed: {
    annotators() {
      const unique = new Set(this.reportData.map(r => r.user))
      return [...unique].map(u => ({ user: u }))
    },
    filteredResults() {
      return this.reportData.filter(r => {
        const inUser = this.filters.annotator
          ? r.user === this.filters.annotator
          : true
        const inStart = this.filters.start
          ? new Date(r.created_at) >= new Date(this.filters.start)
          : true
        const inEnd = this.filters.end
          ? new Date(r.created_at) <= new Date(this.filters.end)
          : true
        return inUser && inStart && inEnd
      })
    }
  },
  watch: {
    selectedReportId() {
      this.fetchReportData()
    }
  },
  async mounted() {
    this.fetchReports()
    try {
      const project = await this.$axios.$get(`/api/projects/${this.$route.params.id}/`)
      this.projectName = project.name
    } catch (e) {
      this.projectName = 'Projeto'
    }
  },
  methods: {
    async fetchReports() {
      try {
        const res = await this.$axios.$get('/api/reports/', {
          params: { project_id: this.$route.params.id }
        })
        this.reports = res.reverse()
      } catch (e) {
        console.error('Erro ao carregar relatórios:', e)
        this.error = null
      }
    },
    async generateReport() {
      try {
        const payload = { project_id: this.$route.params.id }
        await this.$axios.$post('/api/reports/', payload)

        const res = await this.$axios.$get('/api/reports/', {
          params: { project_id: this.$route.params.id }
        })

        this.reports = res.reverse()
        this.selectedReportId = this.reports[0].id
        await this.fetchReportData()

      } catch (e) {
        console.error('Erro ao gerar novo relatório:', e)
        this.error = null
      }
    },
    async fetchReportData() {
      if (!this.selectedReportId) return

      try {
        const res = await this.$axios.$get(
          `/api/reports/${this.selectedReportId}/data/`
        )

        if (!res.results.length) {
          const members = await this.$axios.$get(
            `/api/projects/${this.$route.params.id}/members/`
          )

          if (!members.length) {
            this.reportData = [{
              id: '-',
              text: '-',
              user: 'Sem utilizadores',
              created_at: '-',
              project: this.projectName,
              perspective: '-'
            }]
          } else {
            this.reportData = members.map(member => ({
              id: '-',
              text: '-',
              user: member.username,
              created_at: '-',
              project: this.projectName,
              perspective: '-'
            }))
          }
        } else {
          this.reportData = res.results
        }
      } catch (e) {
        console.error('Erro ao carregar dados do relatório:', e)
        this.reportData = [{
          id: '-',
          text: '-',
          user: 'Erro ao carregar dados do relatório',
          created_at: '-',
          project: this.projectName,
          perspective: '-'
        }]
        this.error = null
      }
    },
    exportCSV() {
      const headers = this.headers.map(h => h.text)
      const rows = this.filteredResults.map(r => [
        r.id,
        r.text.replace(/\n/g, ' '),
        r.user,
        r.created_at,
        r.project,
        r.perspective ?? ''
      ])
      const csv = [headers, ...rows]
        .map(row => row.map(v => `"${v}"`).join(','))
        .join('\n')
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.setAttribute('download', 'relatorio.csv')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }
}
</script>
