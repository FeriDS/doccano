<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Annotation Statistics</h1>
        <v-alert type="info" outlined class="mb-4">
          <div class="text-body-1 font-weight-bold mb-1">Sobre estas estatísticas</div>
          <div>
            Esta página apresenta estatísticas detalhadas sobre as anotações do projeto, incluindo:
            <ul>
              <li><b>Taxa de desacordo entre anotadores</b>: 
              identifica casos em que diferentes anotadores discordam sobre a mesma anotação.</li>
              <li><b>Diversidade de perspetivas</b>: 
              mostra quantas perspetivas diferentes foram registradas nas anotações.</li>
              <li><b>Taxa de resolução de desacordos</b>: 
              indica quantos desacordos já foram resolvidos colaborativamente.</li>
            </ul>
            Utilize os filtros para refinar a análise por período,
             anotador ou perspetiva. Os gráficos e tabelas ajudam a identificar padrões,
              promover discussões e melhorar a qualidade das anotações.
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Filters Section -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Filters</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-menu
                  ref="startDateMenu"
                  v-model="filters.startDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template #activator="{ on, attrs }">
                    <v-text-field
                      v-model="filters.startDate"
                      label="Start Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="filters.startDate"
                    @input="filters.startDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>

              <v-col cols="12" md="3">
                <v-menu
                  ref="endDateMenu"
                  v-model="filters.endDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template #activator="{ on, attrs }">
                    <v-text-field
                      v-model="filters.endDate"
                      label="End Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="filters.endDate"
                    @input="filters.endDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.annotator"
                  :items="annotators"
                  item-text="username"
                  item-value="id"
                  label="Annotator"
                  clearable
                ></v-select>
              </v-col>

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.perspective"
                  :items="perspectives"
                  label="Perspective"
                  clearable
                ></v-select>
              </v-col>

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.label"
                  :items="categories"
                  item-text="text"
                  item-value="text"
                  label="Categoria"
                  clearable
                ></v-select>
              </v-col>

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.resolved"
                  :items="statusOptions"
                  label="Status de Resolução"
                  clearable
                ></v-select>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Statistics Overview -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Disagreement Rate</v-card-title>
          <v-card-text>
            <div class="text-h4">{{ statistics.disagreementRate }}%</div>
            <div class="text-subtitle-2">Percentage of annotations with disagreements</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Perspective Diversity</v-card-title>
          <v-card-text>
            <div class="text-h4">{{ statistics.perspectiveCount }}</div>
            <div class="text-subtitle-2">Unique perspectives used</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Resolution Rate</v-card-title>
          <v-card-text>
            <div class="text-h4">{{ statistics.resolutionRate }}%</div>
            <div class="text-subtitle-2">Disagreements resolved</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Detailed Statistics -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Tempo médio de anotação</v-card-title>
          <v-card-text>
            <div class="text-h4">{{ statistics.averageAnnotationTime }}s</div>
            <div class="text-subtitle-2">Tempo médio entre início e conclusão das anotações</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Distribuição de Labels</v-card-title>
          <v-card-text>
            <canvas ref="labelDistChart"></canvas>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Padrões por Perspetiva</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="perspectiveHeaders"
              :items="perspectivePatterns"
              class="elevation-1"
              disable-pagination
              hide-default-footer
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Disagreement Details -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Disagreement Details
            <v-spacer></v-spacer>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>
          <v-data-table
            :headers="headers"
            :items="disagreements"
            :search="search"
            :loading="loading"
            class="elevation-1"
          >
            <template #[`item.actions`]="{ item }">
              <v-btn
                small
                color="primary"
                @click="viewDisagreement(item)"
              >
                View Details
              </v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Disagreement Dialog -->
    <v-dialog v-model="dialog" max-width="800px">
      <v-card>
        <v-card-title>
          <span class="text-h5">Disagreement Details</span>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <h3>Text Content</h3>
              <p>{{ selectedDisagreement.text }}</p>
            </v-col>
            <v-col cols="12">
              <h3>Annotations</h3>
              <v-list>
                <v-list-item 
                  v-for="annotation in selectedDisagreement.annotations" 
                  :key="annotation.id"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ annotation.annotator }}</v-list-item-title>
                    <v-list-item-subtitle>
                      Label: {{ annotation.label }}
                      <br>
                      Perspective: {{ annotation.perspective }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12">
              <h3>Discussion</h3>
              <v-list>
                <v-list-item 
                  v-for="comment in selectedDisagreement.discussion" 
                  :key="comment.id"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ comment.user }}</v-list-item-title>
                    <v-list-item-subtitle>{{ comment.text }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import Chart from 'chart.js'

export default {
  name: 'AnnotationStatistics',

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      filters: {
        startDate: null,
        endDate: null,
        annotator: null,
        perspective: null,
        label: null,
        resolved: null,
        startDateMenu: false,
        endDateMenu: false
      },
      statistics: {
        disagreementRate: 0,
        perspectiveCount: 0,
        resolutionRate: 0,
        averageAnnotationTime: 0
      },
      disagreements: [],
      search: '',
      loading: false,
      dialog: false,
      selectedDisagreement: {},
      headers: [
        { text: 'Text ID', value: 'textId' },
        { text: 'Texto', value: 'text', width: '30%' },
        { text: 'Category', value: 'category' },
        { text: 'Disagreement Type', value: 'type' },
        { text: 'Annotators', value: 'annotators' },
        { text: 'Status', value: 'status' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      annotators: [],
      perspectives: [],
      categories: [],
      statusOptions: [
        { text: 'Todos', value: null },
        { text: 'Resolvidos', value: 'true' },
        { text: 'Não resolvidos', value: 'false' }
      ],
      perspectivePatterns: [],
      perspectiveHeaders: [
        { text: 'Perspetiva', value: 'perspective' },
        { text: 'Total', value: 'total' },
        { text: 'Desacordos', value: 'disagreements' },
        { text: 'Acordos', value: 'agreements' }
      ]
    }
  },

  computed: {
    projectId() {
      return this.$route.params.id
    }
  },

  watch: {
    filters: {
      deep: true,
      handler() {
        this.fetchStatistics()
      }
    }
  },

  async created() {
    await this.fetchAnnotators()
    await this.fetchPerspectives()
    await this.fetchCategories()
    await this.fetchStatistics()
  },

  mounted() {
    this.initializeCharts()
  },

  methods: {
    async fetchAnnotators() {
      try {
        const response = await this.$repositories.user.list(this.projectId)
        this.annotators = response.data
      } catch (error) {
        console.error('Error fetching annotators:', error)
      }
    },

    async fetchPerspectives() {
      try {
        const response = await this.$repositories.perspective.list(this.projectId)
        this.perspectives = response.data
      } catch (error) {
        console.error('Error fetching perspectives:', error)
      }
    },

    async fetchCategories() {
      try {
        const response = await this.$services.categoryType.list(this.projectId)
        this.categories = response
      } catch (error) {
        console.error('Erro ao buscar categorias:', error)
      }
    },

    async fetchStatistics() {
      this.loading = true
      try {
        const params = {}
        if (this.filters.startDate) params.start_date = this.filters.startDate
        if (this.filters.endDate) params.end_date = this.filters.endDate
        if (this.filters.annotator) params.annotator = this.filters.annotator
        if (this.filters.perspective) params.perspective = this.filters.perspective
        if (this.filters.label) params.label = this.filters.label
        if (this.filters.resolved !== null) params.resolved = this.filters.resolved

        if (!this.$repositories || !this.$repositories.statistics) {
          throw new Error('Repositório de estatísticas não está disponível.')
        }
        const response = await this.$repositories.statistics.fetchAnnotationStatistics(
          this.projectId,
          params
        )
        this.statistics = response.data.statistics
        this.disagreements = response.data.disagreements
        this.perspectivePatterns = response.data.perspectivePatterns || []
        this.updateCharts(response.data)
      } catch (error) {
        console.error('Error fetching statistics:', error)
      } finally {
        this.loading = false
      }
    },

    initializeCharts() {
      if (this.$refs.disagreementChart) {
        const disagreementCtx = this.$refs.disagreementChart.getContext('2d')
        this.disagreementChart = new Chart(disagreementCtx, {
          type: 'bar',
          data: {
            labels: [],
            datasets: [{
              label: 'Disagreements by Category',
              data: [],
              backgroundColor: 'rgba(255, 99, 132, 0.5)'
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        })
      }
      if (this.$refs.perspectiveChart) {
        const perspectiveCtx = this.$refs.perspectiveChart.getContext('2d')
        this.perspectiveChart = new Chart(perspectiveCtx, {
          type: 'pie',
          data: {
            labels: [],
            datasets: [{
              data: [],
              backgroundColor: [
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)',
                'rgba(255, 159, 64, 0.5)'
              ]
            }]
          },
          options: {
            responsive: true
          }
        })
      }
      if (this.$refs.labelDistChart) {
        const labelDistCtx = this.$refs.labelDistChart.getContext('2d')
        this.labelDistChart = new Chart(labelDistCtx, {
          type: 'pie',
          data: {
            labels: [],
            datasets: [{
              data: [],
              backgroundColor: [
                'rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)',
                'rgba(255, 159, 64, 0.5)'
              ]
            }]
          },
          options: {
            responsive: true
          }
        })
      }
    },

    updateCharts(data) {
      // Update disagreement chart
      if (this.disagreementChart && data.disagreementByCategory) {
        this.disagreementChart.data.labels = 
          data.disagreementByCategory.map(item => item.category)
        this.disagreementChart.data.datasets[0].data = 
          data.disagreementByCategory.map(item => item.count)
        this.disagreementChart.update()
      }
      // Update perspective chart
      if (this.perspectiveChart && data.perspectiveDistribution) {
        this.perspectiveChart.data.labels = 
          data.perspectiveDistribution.map(item => item.perspective)
        this.perspectiveChart.data.datasets[0].data = 
          data.perspectiveDistribution.map(item => item.count)
        this.perspectiveChart.update()
      }
      // Update label distribution chart
      if (this.labelDistChart && data.labelDistribution) {
        const labelDist = data.labelDistribution || {}
        this.labelDistChart.data.labels = Object.keys(labelDist)
        this.labelDistChart.data.datasets[0].data = Object.values(labelDist)
        this.labelDistChart.update()
      }
    },

    viewDisagreement(item) {
      this.selectedDisagreement = item
      this.dialog = true
    }
  }
}
</script> 