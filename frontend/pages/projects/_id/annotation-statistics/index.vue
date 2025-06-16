<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" class="d-flex align-center justify-space-between">
        <h1 class="text-h4 mb-4">Annotation Statistics</h1>
        <v-btn
          class="return-btn"
          @click="$router.back()"
          title="Return"
          outlined
          color="black"
        >
          <v-icon left color="black">mdi-arrow-left</v-icon>
          <span style="font-weight: 600; letter-spacing: 1px;">RETURN</span>
        </v-btn>
      </v-col>
    </v-row>

    <!-- Filters Section -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Filters
            <v-spacer></v-spacer>
            <v-btn
              icon
              title="Clear all filters"
              class="clear-filters-btn"
              style="display: flex; align-items: center;"
              @click="clearFilters"
            >
              <v-icon color="black" size="32">mdi-close</v-icon>
              <span
                style="color: #222; font-weight: 500; margin-left: 1px; font-size: 12px;"
              >
                Cancel
              </span>
            </v-btn>
          </v-card-title>
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
                  v-model="filters.selectedPerspective"
                  :items="perspectives"
                  item-text="name"
                  item-value="name"
                  label="Perspectiva"
                  clearable
                  @change="onPerspectiveChange"
                />
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

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.example"
                  :items="examples"
                  item-text="text"
                  item-value="id"
                  label="Texto/Example"
                  clearable
                />
              </v-col>

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.finished"
                  :items="[
                    { text: 'Todos', value: null },
                    { text: 'Fechados', value: 'true' },
                    { text: 'Abertos', value: 'false' }
                  ]"
                  label="Status de Fechamento"
                  clearable
                />
              </v-col>

              <v-col v-for="field in choicePerspectiveFields" :key="field.name" cols="12" md="3">
                <v-select
                  v-model="filters.perspective"
                  :items="field.choices"
                  :label="field.name"
                  clearable
                />
              </v-col>

              <v-col v-for="field in numberPerspectiveFields" :key="field.name" cols="12" md="3">
                <v-text-field
                  v-model="filters.perspectiveValues[field.name]"
                  :label="field.name"
                  type="number"
                  clearable
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Detailed Statistics -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Label Distribution</v-card-title>
          <v-card-text>
            <canvas ref="labelDistChart"></canvas>
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
              <v-btn
                v-if="item.status !== 'resolved'"
                small
                color="success"
                @click="resolveDisagreement(item)"
                
              >
                Resolver
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
import { mdiArrowLeft } from '@mdi/js'

export default {
  name: 'AnnotationStatistics',

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      filters: {
        startDate: null,
        endDate: null,
        selectedPerspective: null,
        perspective: null,
        label: null,
        resolved: null,
        example: null,
        finished: null,
        startDateMenu: false,
        endDateMenu: false,
        perspectiveValues: {},
        mdiArrowLeft
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
      perspectives: [],
      projectPerspective: null,
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
      ],
      examples: [],
      perspectiveFields: [],
      perspectiveChoices: []
    }
  },

  computed: {
    projectId() {
      return this.$route.params.id
    },
    choicePerspectiveFields() {
      return this.perspectiveFields.filter(f => f.field_type === 'choice')
    },
    numberPerspectiveFields() {
      return this.perspectiveFields.filter(f => f.field_type === 'number')
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
    await this.fetchProjectPerspective()
    await this.fetchCategories()
    await this.fetchExamples()
    await this.fetchStatistics()
  },

  mounted() {
    this.initializeCharts()
  },

  methods: {
    async fetchProjectPerspective() {
      try {
        const response = await this.$repositories.perspective.getProjectPerspective(this.projectId)
        if (response && response.perspective) {
          this.projectPerspective = response.perspective
          this.perspectiveFields = response.perspective.fields || []
          this.perspectives = [response.perspective]
        } else {
          this.perspectiveFields = []
          this.perspectives = []
        }
      } catch (e) {
        this.perspectiveFields = []
        this.perspectives = []
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

    async fetchExamples() {
      try {
        const response = await this.$services.example.list(this.projectId, {})
        this.examples = response.items
      } catch (error) {
        console.error('Erro ao buscar exemplos:', error)
      }
    },

    async fetchStatistics() {
      this.loading = true
      try {
        const params = {}
        if (this.filters.startDate) params.start_date = this.filters.startDate
        if (this.filters.endDate) params.end_date = this.filters.endDate
        if (this.filters.perspective) params.perspective = this.filters.perspective
        if (this.filters.label) params.label = this.filters.label
        if (this.filters.resolved !== null) params.resolved = this.filters.resolved
        if (this.filters.example) params.example_id = this.filters.example
        if (this.filters.finished !== null) params.finished = this.filters.finished
        Object.entries(this.filters.perspectiveValues).forEach(([key, value]) => {
          if (value) params[`perspective_${key}`] = value
        })

        if (!this.$repositories || !this.$repositories.statistics) {
          throw new Error('Repositório de estatísticas não está disponível.')
        }
        const response = await this.$repositories.statistics.fetchAnnotationStatistics(
          this.projectId,
          params
        )
        this.statistics = response.statistics
        this.disagreements = response.disagreements
        this.perspectivePatterns = response.perspectivePatterns || []
        this.updateCharts(response)
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
    },

    async resolveDisagreement(item) {
      try {
        await this.$services.example.resolve(this.projectId, item.id)
        this.$toast && this.$toast.success('Desacordo resolvido!')
        await this.fetchStatistics()
      } catch (error) {
        this.$toast && this.$toast.error('Erro ao resolver desacordo')
        console.error('Erro ao resolver desacordo:', error)
      }
    },

    onPerspectiveChange() {
      this.filters.perspective = null
    },

    clearFilters() {
      this.filters = {
        startDate: null,
        endDate: null,
        selectedPerspective: null,
        perspective: null,
        label: null,
        resolved: null,
        example: null,
        finished: null,
        startDateMenu: false,
        endDateMenu: false,
      }
    }
  }
}
</script>

<style scoped>
.clear-filters-btn {
  background: transparent !important;
  border: none !important;
  box-shadow: none;
  border-radius: 6px !important;
  margin-right: 8px;
}

.return-btn {
  text-transform: uppercase;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  margin-left: 16px;
}
</style> 