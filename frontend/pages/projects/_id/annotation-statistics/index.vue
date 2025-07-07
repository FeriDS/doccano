<template>
  <v-container fluid>
    <v-row align="center" class="mb-4">
      <v-col>
        <h1 class="text-h4">Statistics by Text</h1>
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="success"
          :loading="exportingCSV"
          class="mr-2"
          @click="exportCSV"
        >
          <v-icon left>mdi-file-excel</v-icon>
          Export CSV
        </v-btn>
        <v-btn
          color="error"
          :loading="exportingPDF"
          @click="exportPDF"
        >
          <v-icon left>mdi-file-pdf</v-icon>
          Export PDF
        </v-btn>
        <v-btn color="info" :loading="exportingXLSX" class="mr-2" @click="exportXLSX">
          <v-icon left>mdi-file-excel</v-icon>
          Export XLSX
        </v-btn>
        <v-btn text aria-label="Return" @click="$router.back()">
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </v-col>
    </v-row>
          <v-alert
        type="info"
        class="mb-4"
        :value="true"
      >
        <strong>Note:</strong> Only finalized datasets are displayed on this page.
        <br>
        <strong>Total finalized datasets:</strong> {{ examples.length }}
        <br>
        <strong>Export:</strong> 
        <ul>
          <li><strong>CSV:</strong> Tabular data with label distribution per example</li>
          <li><strong>XLSX:</strong> Tabular data + visual charts</li>
          <li><strong>PDF:</strong> Full report with charts and detailed statistics</li>
        </ul>
      </v-alert>

    <!-- Filtros -->
    <v-card class="mb-6">
      <v-card-title>
        <v-icon left>mdi-filter</v-icon>
        Filters
        <v-chip
          v-if="hasActiveFilters"
          color="primary"
          small
          class="ml-2"
        >
          {{ activeFiltersCount }} active filter(s)
        </v-chip>
        <v-spacer />
        <v-switch
          v-model="useLocalFiltering"
          label="Local Filter"
          class="ml-4"
        />
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <div v-if="projectPerspective">
              <strong>Perspective:</strong> {{ projectPerspective.name }}
            </div>
          </v-col>
        </v-row>
        <v-row>
          
          <template v-if="perspectiveFields && perspectiveFields.length">
            <template v-for="field in perspectiveFields">
              <v-col :key="field.id" cols="12" md="4">
                <v-select
                  v-model="filters.perspectiveValues[field.id]"
                  :label="field.name"
                  :items="field.choices"
                  clearable
                  :disabled="!useLocalFiltering"
                />
              </v-col>
            </template>
          </template>
        </v-row>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.resolved"
              :items="statusOptions"
              item-text="text"
              item-value="value"
              label="Status"
              clearable
              :disabled="!useLocalFiltering"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.label"
              :items="filteredCategories"
              item-text="text"
              item-value="id"
              label="Labels"
              clearable
              multiple
              :disabled="!useLocalFiltering"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.example"
              :items="(allExamples.length ? allExamples :
               examples).map(e => ({ text: e.text, value: e.id }))"
              item-text="text"
              item-value="value"
              label="Example"
              clearable
              :return-object="false"
              multiple
              :disabled="!useLocalFiltering"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" md="3">
            <v-menu
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
                  clearable
                  v-on="on"
                  :disabled="!useLocalFiltering"
                />
              </template>
              <v-date-picker
                v-model="filters.startDate"
                @input="filters.startDateMenu = false"
              />
            </v-menu>
          </v-col>
          <v-col cols="12" md="3">
            <v-menu
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
                  clearable
                  v-on="on"
                  :disabled="!useLocalFiltering"
                />
              </template>
              <v-date-picker
                v-model="filters.endDate"
                @input="filters.endDateMenu = false"
              />
            </v-menu>
          </v-col>
          <v-col cols="12" md="3">
            <v-btn
              color="primary"
              :loading="loading"
              @click="applyFilters"
              :disabled="!useLocalFiltering"
            >
              <v-icon left>mdi-filter-check</v-icon>
              Apply Filters
            </v-btn>
          </v-col>
          <v-col cols="12" md="3">
            <v-btn
              outlined
              @click="clearFilters"
              :disabled="!useLocalFiltering"
            >
              <v-icon left>mdi-filter-remove</v-icon>
              Clear Filters
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <div v-for="example in examples" :key="example.id" class="mb-6">
      <v-card class="mb-4">
        <v-card-title class="text-h6">
          {{ example.text }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="6">
              <h3 class="text-h6 mb-3">Label Distribution</h3>
              
              <div style="min-height: 250px;">
                <canvas :ref="'labelsChart' + example.id"></canvas>
              </div>
            </v-col>
            <v-col cols="6">
              <h3 class="text-h6 mb-3">Abstention and Null</h3>
              <div style="min-height: 250px;">
                <canvas :ref="'abstractionChart' + example.id"></canvas>
              </div>
            </v-col>
          </v-row>
          <v-row class="mt-4">
            <v-col cols="12">
              <v-card outlined class="pa-3">
                <v-row>
                  <v-col cols="6" class="text-center">
                    <div class="text-h6 text-blue-darken-2 font-weight-bold">
                      Total Regular Labels: <span :id="'summary-labels-' + example.id">0%</span>
                    </div>
                  </v-col>
                  <v-col cols="6" class="text-center">
                    <div class="text-h6 text-red-darken-2 font-weight-bold">
                      Total non-voted: <span :id="'summary-abstention-' + example.id">0%</span>
                    </div>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>
    
    <!-- Botão Return no final da página -->
    <v-row class="mt-6">
      <v-col class="text-right">
        <v-btn text aria-label="Return" @click="$router.back()">
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </v-col>
    </v-row>
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
      mdiArrowLeft, 
      filters: {
        startDate: null,
        endDate: null,
        selectedPerspective: null,
        perspective: null,
        perspectiveValue: null,
        label: [],
        resolved: null,
        example: [],
        finished: null,
        startDateMenu: false,
        endDateMenu: false,
        perspectiveValues: {},
        
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
        { text: 'All', value: null },
        { text: 'resolved', value: 'true' },
        { text: 'non-resolved', value: 'false' }
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
      perspectiveChoices: [],
      allExamplesData: [],
      expandedPanels: [],
      charts: {},
      labelsCharts: {},
      abstractionCharts: {},
      useLocalFiltering: false,
      allExamples: [], // Para armazenar todos os exemplos quando usar filtro local
      exportingCSV: false,
      exportingPDF: false,
      exportingXLSX: false
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
    },
    hasActiveFilters() {
      return this.filters.startDate || 
             this.filters.endDate || 
             this.filters.perspective || 
             this.filters.label.length > 0 || 
             this.filters.resolved !== null ||
             Object.keys(this.filters.perspectiveValues).length > 0
    },
    activeFiltersCount() {
      let count = 0
      if (this.filters.startDate) count++
      if (this.filters.endDate) count++
      if (this.filters.perspective) count++
      if (this.filters.label.length > 0) count++
      if (this.filters.resolved !== null) count++
      count += Object.keys(this.filters.perspectiveValues).length
      return count
    },
    filteredCategories() {
      return this.categories;
    },
    screenExamples() {
      return this.examples.map(e => ({
        id: e.id,
        text: e.text,
        labelsChartData: {
          labels: this.labelsCharts[e.id]?.data.labels || [],
          data: this.labelsCharts[e.id]?.data.datasets[0]?.data || []
        },
        abstractionChartData: {
          labels: this.abstractionCharts[e.id]?.data.labels || [],
          data: this.abstractionCharts[e.id]?.data.datasets[0]?.data || []
        }
      }));
    }
  },

  watch: {
    filters: {
      deep: true,
      handler() {
        this.fetchStatistics()
      }
    },
    examples: {
      handler() {
        this.$nextTick(async () => {
          await this.renderAllCharts()
        })
      }
    },
    useLocalFiltering() {
      // Recarregar dados quando alternar entre filtro local e API
      this.applyFilters()
    }
  },

  async created() {
    await this.fetchProjectPerspective()
    await this.fetchCategories()
    await this.fetchExamples()
    await this.fetchAllExamplesData()
    await this.fetchStatistics()
  },

  mounted() {
    this.initializeCharts()
    this.$nextTick(async () => {
      await this.renderAllCharts()
    })
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
        console.log('Raw categories response:', response)
        
        this.categories = response.map(cat => {
          const category = {
            text: cat.text || cat.name || cat.label || cat.id,
            id: cat.id
          }
          console.log('Processed category:', category)
          return category
        })
        
        console.log('Final categories:', this.categories)
      } catch (error) {
        console.error('Erro ao buscar categorias:', error)
        this.categories = []
      }
    },

    async fetchExamples() {
      try {
        if (this.useLocalFiltering) {
          // Filtro local - buscar todos e filtrar no frontend
          const response = await this.$services.example.list(this.projectId, {})
          this.allExamples = response.items.filter((it) => it.is_finished)
          
          console.log('DEBUG ALL EXAMPLES:', this.allExamples);
          // Aplicar filtros localmente
          this.examples = this.allExamples.filter(example => {
            console.log('DEBUG EXAMPLE OBJ................:', example);
            // Filtro por data de início
            if (this.filters.startDate) {
              const dateField = example.annotation_start_date
              if (dateField) {
                const exampleDate = new Date(dateField).toISOString().split('T')[0]
                if (exampleDate !== this.filters.startDate) return false
              } else {
                return false
              }
            }
            // Filtro por data de fim
            if (this.filters.endDate) {
              const dateField = example.annotation_end_date
              if (dateField) {
                const exampleDate = new Date(dateField).toISOString().split('T')[0]
                if (exampleDate !== this.filters.endDate) return false
              } else {
                return false
              }
            }
            
            // Filtro por perspetiva (se aplicável)
            if (this.filters.perspective && example.perspective_id) {
              if (example.perspective_id !== this.filters.perspective) return false
            }
            
            // Filtro por categoria (se aplicável)
            if (this.filters.label.length > 0) {
              let hasCategory = false;

              const selectedCategories = this.categories.filter(
                cat => this.filters.label.includes(cat.id) || this.filters.label.includes(cat.text)
              );
              const selectedCategoryIds = selectedCategories.map(cat => String(cat.id));
              const selectedCategoryTexts = selectedCategories.map(cat => String(cat.text));

              // LOGS PARA DEBUG
              console.log('Filtro categoria:', this.filters.label);
              console.log('selectedCategories:', selectedCategories);
              console.log('selectedCategoryIds:', selectedCategoryIds);
              console.log('selectedCategoryTexts:', selectedCategoryTexts);
              console.log('label_distribution:', example.label_distribution);
              console.log('labels:', example.labels);

              if (example.label_distribution) {
                hasCategory = Object.keys(example.label_distribution).some(categoryName => {
                  console.log('Comparando chave:', categoryName, 'com', selectedCategoryIds, selectedCategoryTexts);
                  return (
                    selectedCategoryIds.includes(categoryName) ||
                    selectedCategoryTexts.includes(categoryName)
                  );
                });
              }

              if (!hasCategory && example.labels && Array.isArray(example.labels)) {
                hasCategory = example.labels.some(label => {
                  const labelCategoryId = String(label.category_id || label.category);
                  console.log('Comparando label:', labelCategoryId, 'com', selectedCategoryIds, selectedCategoryTexts);
                  return (
                    selectedCategoryIds.includes(labelCategoryId) ||
                    selectedCategoryTexts.includes(labelCategoryId)
                  );
                });
              }

              if (!hasCategory) return false;
            }
            
            // Filtro por status (se aplicável)
            console.log('Filtro status:', this.filters.resolved, typeof this.filters.resolved);
            console.log('Exemplo is_resolved:', example.is_resolved, typeof example.is_resolved);
            if (this.filters.resolved !== null && this.filters.resolved !== undefined) {
              const filterValue = this.filters.resolved === true || this.filters.resolved === "true" || this.filters.resolved === 1 || this.filters.resolved === "1";
              const exampleValue = example.is_resolved === true || example.is_resolved === "true" || example.is_resolved === 1 || example.is_resolved === "1";
              console.log('Comparando:', exampleValue, 'com', filterValue);
              if (exampleValue !== filterValue) {
                return false;
              }
            }
            
            // Filtro por valores dos fields da perspectiva
            if (this.filters.perspective && this.filters.perspectiveValues) {
              const fields = Object.entries(this.filters.perspectiveValues);
              for (const [fieldId, value] of fields) {
                if (value && (!example.perspective_fields ||
                 example.perspective_fields[fieldId] !== value)) {
                  return false;
                }
              }
            }
            
            // Filtro por exemplo (texto)
            if (this.filters.example && this.filters.example.length) {
              if (!this.filters.example.includes(example.id)) return false
            }
            
            return true
          })
        } else {
          // Filtro via API
          const params = {}
          
          if (this.filters.startDate && this.filters.startDate.trim()) {
            params.created_at = this.filters.startDate
          }
          if (this.filters.endDate && this.filters.endDate.trim()) {
            params.updated_at = this.filters.endDate
          }
          if (this.filters.perspective) {
            params.perspective = this.filters.perspective
          }
          if (this.filters.label.length > 0) {
            params.label = this.filters.label.join(',')
          }
          if (this.filters.resolved !== null && this.filters.resolved !== undefined) {
            params.resolved = this.filters.resolved
          }

          // Adicionar filtros específicos de campos de perspectiva
          Object.entries(this.filters.perspectiveValues).forEach(([fieldId, value]) => {
            if (value) {
              params[`perspective_${fieldId}`] = value
            }
          })

          console.log('Fetching examples with params:', params)
          const response = await this.$services.example.list(this.projectId, params)
          this.examples = response.items.filter((it) => it.is_finished)
        }
        
        // Processar label_distribution para todos os exemplos
        this.examples = this.examples.map((it) => ({
          ...it,
          label_distribution: Object.fromEntries(
            Object.entries(it.label_distribution || {}).map(([l, v]) => {
              const p = Number(v)
              return [l, (p > 1 ? p : p * 100).toFixed(2)]
            })
          )
        }))
        
        console.log('Filtered examples:', this.examples.length)
      } catch (error) {
        console.error('Error fetching examples:', error)
        this.examples = []
      }
    },

    async fetchAllExamplesData() {
      try {
        // Construir parâmetros de filtro
        const params = { limit: 1000 }
        if (this.filters.startDate) params.start_date = this.filters.startDate
        if (this.filters.endDate) params.end_date = this.filters.endDate
        if (this.filters.perspective) params.perspective = this.filters.perspective
        if (this.filters.label.length > 0) params.label = this.filters.label.join(',')
        if (this.filters.resolved !== null) params.resolved = this.filters.resolved

        const response = await this.$services.example.list(this.projectId, params)
        this.allExamplesData = (response.items || [])
          .filter((it) => it.is_finished) // Filtrar apenas datasets finalizados
      } catch (error) {
        console.error('Erro ao buscar dados de todos os exemplos:', error)
        this.allExamplesData = []
      }
    },

    async fetchStatistics() {
      this.loading = true
      try {
        const params = {}
        if (this.filters.startDate) params.start_date = this.filters.startDate
        if (this.filters.endDate) params.end_date = this.filters.endDate
        if (this.filters.perspective) params.perspective = this.filters.perspective
        if (this.filters.label.length > 0) params.label = this.filters.label.join(',')
        if (this.filters.resolved !== null) params.resolved = this.filters.resolved
        if (this.filters.example) params.example_id = this.filters.example
        if (this.filters.finished !== null) params.finished = this.filters.finished
        
        // Adicionar filtros específicos de campos de perspectiva
        Object.entries(this.filters.perspectiveValues).forEach(([fieldId, value]) => {
          if (value) {
            params[`perspective_${fieldId}`] = value
          }
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
      // All Examples Chart
      if (this.$refs.allExamplesChart) {
        const allExamplesCtx = this.$refs.allExamplesChart.getContext('2d')
        this.allExamplesChart = new Chart(allExamplesCtx, {
          type: 'bar',
          data: {
            labels: [],
            datasets: [{
              label: 'Examples Count',
              data: [],
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        })
      }

      // Label Distribution Chart (now bar chart)
      if (this.$refs.labelDistChart) {
        const labelDistCtx = this.$refs.labelDistChart.getContext('2d')
        this.labelDistChart = new Chart(labelDistCtx, {
          type: 'bar',
          data: {
            labels: [],
            datasets: [{
              label: 'Label Distribution',
              data: [],
              backgroundColor: 'rgba(255, 99, 132, 0.8)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label(context) {
                    return context.parsed.y.toFixed(2) + '%'
                  }
                }
              }
            },
            animation: {
              onComplete() {
                const ctx = this.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.font = '12px Arial';
                ctx.fillStyle = '#000';
                this.data.datasets.forEach(function(dataset) {
                  for (let i = 0; i < dataset.data.length; i++) {
                    const model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                    ctx.fillText(dataset.data[i].toFixed(1) + '%', model.x, model.y + 15);
                  }
                });
              }
            }
          }
        })
      }

      // Perspective Chart (now bar chart)
      if (this.$refs.perspectiveChart) {
        const perspectiveCtx = this.$refs.perspectiveChart.getContext('2d')
        this.perspectiveChart = new Chart(perspectiveCtx, {
          type: 'bar',
          data: {
            labels: [],
            datasets: [{
              label: 'Perspective Distribution',
              data: [],
              backgroundColor: 'rgba(75, 192, 192, 0.8)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
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

      // Disagreement Chart
      if (this.$refs.disagreementChart) {
        const disagreementCtx = this.$refs.disagreementChart.getContext('2d')
        this.disagreementChart = new Chart(disagreementCtx, {
          type: 'bar',
          data: {
            labels: [],
            datasets: [{
              label: 'Disagreements by Category',
              data: [],
              backgroundColor: 'rgba(255, 159, 64, 0.8)',
              borderColor: 'rgba(255, 159, 64, 1)',
              borderWidth: 1
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
    },

    updateCharts(data) {
      // Update all examples chart
      if (this.allExamplesChart && this.allExamplesData.length > 0) {
        const exampleLabels = this.allExamplesData.map((_example, index) => `Example ${index + 1}`)
        const exampleData = this.allExamplesData.map(example => {
          // Count annotations for this example
          return example.annotations ? example.annotations.length : 0
        })
        
        this.allExamplesChart.data.labels = exampleLabels
        this.allExamplesChart.data.datasets[0].data = exampleData
        this.allExamplesChart.update()
      }

      // Update label distribution chart (now bar chart)
      if (this.labelDistChart && data.labelDistribution) {
        const labelDist = data.labelDistribution || {}
        this.labelDistChart.data.labels = Object.keys(labelDist)
        this.labelDistChart.data.datasets[0].data = Object.values(labelDist)
        this.labelDistChart.update()
      }

      // Update perspective chart (now bar chart)
      if (this.perspectiveChart && data.perspectiveDistribution) {
        this.perspectiveChart.data.labels = 
          data.perspectiveDistribution.map(item => item.perspective)
        this.perspectiveChart.data.datasets[0].data = 
          data.perspectiveDistribution.map(item => item.count)
        this.perspectiveChart.update()
      }

      // Update disagreement chart
      if (this.disagreementChart && data.disagreementByCategory) {
        this.disagreementChart.data.labels = 
          data.disagreementByCategory.map(item => item.category)
        this.disagreementChart.data.datasets[0].data = 
          data.disagreementByCategory.map(item => item.count)
        this.disagreementChart.update()
      }
    },

    viewDisagreement(item) {
      this.selectedDisagreement = item
      this.dialog = true
    },

    async resolveDisagreement(item) {
      try {
        await this.$services.example.resolve(this.projectId, item.id)
        if (this.$toast && this.$toast.success) {
          this.$toast.success('Desacordo resolvido!')
        }
        await this.fetchStatistics()
      } catch (error) {
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro ao resolver desacordo')
        }
        console.error('Erro ao resolver desacordo:', error)
      }
    },

    onPerspectiveChange() {
      // Limpar filtros de campos de perspectiva quando a perspectiva for alterada
      this.filters.perspectiveValues = {}
      // Recarregar campos da perspectiva selecionada
      this.fetchProjectPerspective()
    },

    clearFilters() {
      console.log('Clearing all filters')
      this.filters = {
        startDate: null,
        endDate: null,
        selectedPerspective: null,
        perspective: null,
        perspectiveValue: null,
        label: [],
        resolved: null,
        example: [],
        finished: null,
        startDateMenu: false,
        endDateMenu: false,
        perspectiveValues: {},
        mdiArrowLeft: this.filters.mdiArrowLeft
      }
      this.applyFilters()
    },

    async exportCSV() {
      this.exportingCSV = true
      try {
        await this.$nextTick(); // Garante que os gráficos estejam renderizados
        // Debug dos dados dos gráficos
        console.log('DEBUG labelsCharts:', this.labelsCharts);
        console.log('DEBUG abstractionCharts:', this.abstractionCharts);
        console.log('DEBUG examples:', this.examples);
        // Montar screenExamples igual ao exportPDF
        const screenExamples = this.examples.map(e => ({
          id: e.id,
          text: e.text,
          labelsChartData: {
            labels: this.labelsCharts[e.id]?.data.labels || [],
            data: this.labelsCharts[e.id]?.data.datasets[0]?.data || []
          },
          abstractionChartData: {
            labels: this.abstractionCharts[e.id]?.data.labels || [],
            data: this.abstractionCharts[e.id]?.data.datasets[0]?.data || []
          }
        }));
        console.log('DEBUG screenExamples:', screenExamples);
        const params = this.buildExportParams();
        const url = `/v1/projects/${this.projectId}/statistics/export/csv?${params}`;
        const response = await this.$axios.post(url, { screenExamples }, { responseType: 'blob' });
        // Criar link para download
        const blob = new Blob([response.data], { type: 'text/csv; charset=utf-8' })
        const url_download = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url_download
        link.download = `estatisticas_por_texto_${this.projectId}_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url_download)
        if (this.$toast && this.$toast.success) {
          this.$toast.success('Relatório CSV exportado com sucesso!')
        }
      } catch (error) {
        console.error('Erro ao exportar CSV:', error)
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro ao exportar relatório CSV')
        }
      } finally {
        this.exportingCSV = false
      }
    },

    async exportPDF() {
      this.exportingPDF = true
      try {
        await this.$nextTick(); // Garante que os gráficos estejam renderizados
        const chartImages = {};
        // PNG 1x1 px branco
        const blankImg = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+X2ZkAAAAASUVORK5CYII=';
        for (const example of this.examples) {
          let labelsImg = null;
          let abstractionImg = null;
          if (this.labelsCharts[example.id]) {
            try {
              labelsImg = this.labelsCharts[example.id].toBase64Image();
            } catch (e) { labelsImg = null; }
          }
          if (this.abstractionCharts[example.id]) {
            try {
              abstractionImg = this.abstractionCharts[example.id].toBase64Image();
            } catch (e) { abstractionImg = null; }
          }
          if (!labelsImg) labelsImg = blankImg;
          if (!abstractionImg) abstractionImg = blankImg;
          chartImages[example.id] = {
            labels: labelsImg,
            abstraction: abstractionImg
          };
        }
        // Enviar também todos os exemplos exibidos na tela, com os dados dos gráficos
        const screenExamples = this.examples.map(e => ({
          id: e.id,
          text: e.text,
          labelsChartData: {
            labels: this.labelsCharts[e.id]?.data.labels || [],
            data: this.labelsCharts[e.id]?.data.datasets[0]?.data || []
          },
          abstractionChartData: {
            labels: this.abstractionCharts[e.id]?.data.labels || [],
            data: this.abstractionCharts[e.id]?.data.datasets[0]?.data || []
          }
        }));
        const params = this.buildExportParams();
        const url = `/v1/projects/${this.projectId}/statistics/export/pdf?${params}`;
        const response = await this.$axios.post(url, { chartImages, screenExamples }, { responseType: 'blob' });
        // Criar link para download
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url_download = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url_download;
        link.download = `estatisticas_por_texto_${this.projectId}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url_download);
        if (this.$toast && this.$toast.success) {
          this.$toast.success('Relatório PDF exportado com sucesso!');
        }
      } catch (error) {
        console.error('Erro ao exportar PDF:', error);
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro ao exportar relatório PDF');
        }
      } finally {
        this.exportingPDF = false;
      }
    },

    buildExportParams() {
      const params = new URLSearchParams()
      
      // Adicionar filtros ativos
      if (this.filters.startDate) {
        params.append('start_date', this.filters.startDate)
      }
      if (this.filters.endDate) {
        params.append('end_date', this.filters.endDate)
      }
      if (this.filters.label.length > 0) {
        params.append('label', this.filters.label.join(','))
      }
      if (this.filters.resolved !== null && this.filters.resolved !== undefined) {
        params.append('resolved', this.filters.resolved)
      }
      if (this.filters.perspective) {
        params.append('perspective', this.filters.perspective)
      }
      
      // Adicionar filtros específicos de campos de perspectiva
      Object.entries(this.filters.perspectiveValues).forEach(([fieldId, value]) => {
        if (value) {
          params.append(`perspective_${fieldId}`, value)
        }
      })
      
      return params.toString()
    },

    async fetchLabelDistribution(exampleId) {
      try {
        // Construir parâmetros de filtro para a distribuição
        const params = {}
        Object.entries(this.filters.perspectiveValues).forEach(([fieldId, value]) => {
          if (value) {
            params[`perspective_${fieldId}`] = value
          }
        })
        
        // Usar o novo endpoint de distribuição
        const response = await this.$axios.$get(`/v1/projects/${this.projectId}/statistics/discrepancies/${exampleId}/distribution`, { params })
        
        // Logs para debug
        console.log(`Debug - Example ${exampleId} distribution:`, response)
        console.log(`Debug - Filters applied:`, params)
        
        return response
      } catch (error) {
        console.error('Error fetching label distribution:', error)
        return {}
      }
    },

    combineAndSort(labels, data) {
      const combined = labels.map((label, i) => ({ label, value: data[i] }));
      combined.sort((a, b) => a.label.localeCompare(b.label));
      return {
        labels: combined.map(item => item.label),
        data: combined.map(item => item.value)
      };
    },

    renderLabelsChart(exampleId, distribution) {
      // Compatível com novo e antigo formato
      const isNewFormat = distribution && typeof distribution === 'object' && 'labels' in distribution;
      const allLabels = isNewFormat ? Object.keys(distribution.labels || {}) :
       Object.keys(distribution || {});
      const allData = isNewFormat ? Object.values(distribution.labels ||
       {}).map(Number) : Object.values(distribution || {}).map(Number);
      
      // Filtrar apenas labels regulares (excluir abstração e null)
      let regularLabels = [];
      let regularData = [];
      
      allLabels.forEach((label, index) => {
        const value = allData[index];
        // Excluir se contém palavras-chave de abstração ou é null
        if (!label.toLowerCase().includes('abstração') && 
            !label.toLowerCase().includes('abstraction') && 
            !label.toLowerCase().includes('abstenção') &&
            !label.toLowerCase().includes('abstention') &&
            !label.toLowerCase().includes('null') &&
            label !== 'Null' &&
            label !== 'null') {
          regularLabels.push(label);
          regularData.push(value);
        }
      });
      
      // NOVO: Se houver filtro de label, mostrar só ele
      if (this.filters.label.length > 0) {
        const selectedCategories = this.categories.filter(
          cat => this.filters.label.includes(cat.id) || this.filters.label.includes(cat.text)
        );
        const selectedLabels = selectedCategories.map(cat => String(cat.text));
        // Filtra todos os labels selecionados
        const filteredRegularLabels = [];
        const filteredRegularData = [];
        regularLabels.forEach((l, i) => {
          if (selectedLabels.includes(l)) {
            filteredRegularLabels.push(l);
            filteredRegularData.push(regularData[i]);
          }
        });
        regularLabels = filteredRegularLabels;
        regularData = filteredRegularData;
      }

      // Calcular percentagem total de labels regulares
      const totalLabels = regularData.reduce((sum, value) => sum + value, 0);
      
      // Atualizar o elemento HTML com a percentagem total
      this.$nextTick(() => {
        const totalElement = document.getElementById(`total-labels-${exampleId}`);
        if (totalElement) {
          totalElement.textContent = `${totalLabels.toFixed(1)}%`;
        }
        const summaryElement = document.getElementById(`summary-labels-${exampleId}`);
        if (summaryElement) {
          summaryElement.textContent = `${totalLabels.toFixed(1)}%`;
        }
      });
      
      // Ordenar labels e valores
      const sorted = this.combineAndSort(regularLabels, regularData);
      regularLabels = sorted.labels;
      regularData = sorted.data;
      
      const refName = 'labelsChart' + exampleId;
      const ctxArr = this.$refs[refName];
      const ctx = Array.isArray(ctxArr) ? ctxArr[0] : ctxArr;
      if (!ctx) return;
      if (this.labelsCharts[exampleId]) {
        this.labelsCharts[exampleId].destroy();
      }
      this.labelsCharts[exampleId] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: regularLabels,
          datasets: [{
            label: 'Label Distribution (%)',
            data: regularData,
            backgroundColor: 'rgba(54, 162, 235, 0.8)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label(context) {
                  return context.parsed.y.toFixed(2) + '%'
                }
              }
            },
            title: {
              display: true,
              text: `Total Labels: ${totalLabels.toFixed(1)}%`,
              font: {
                size: 26,
                weight: 'bold'
              },
              color: '#1976d2',
              padding: {
                top: 50,
                bottom: 40
              }
            }
          },
          animation: {
            onComplete() {
              const ctx = this.ctx;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.font = '12px Arial';
              ctx.fillStyle = '#000';
              this.data.datasets.forEach(function(dataset) {
                for (let i = 0; i < dataset.data.length; i++) {
                  const model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                  ctx.fillText(dataset.data[i].toFixed(1) + '%', model.x, model.y + 15);
                }
              });
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              min: 0,
              max: 100,
              ticks: { callback: v => v + '%' }
            },
            yAxes: [{
              ticks: {
                beginAtZero: true,
                min: 0,
                max: 100,
                callback: v => v + '%'
              }
            }]
          }
        }
      });
    },

    renderAbstractionChart(exampleId, distribution) {
      console.log(`Debug - Rendering abstraction chart for example ${exampleId}:`, distribution)
      
      // Compatível com novo e antigo formato
      const isNewFormat = distribution && typeof distribution === 'object' && 'labels' in distribution;
      const allLabels = isNewFormat ? Object.keys(distribution.labels || 
      {}) : Object.keys(distribution || {});
      const allData = isNewFormat ? Object.values(distribution.labels ||
       {}).map(Number) : Object.values(distribution || {}).map(Number);
      
      console.log(`Debug - All labels:`, allLabels)
      console.log(`Debug - All data:`, allData)
      
      // Filtrar apenas abstração e null
      let abstractionLabels = [];
      let abstractionData = [];
      
      allLabels.forEach((label, index) => {
        const value = allData[index];
        // Considerar como abstração se contém palavras-chave ou é null
        if (label.toLowerCase().includes('abstração') || 
            label.toLowerCase().includes('abstraction') || 
            label.toLowerCase().includes('abstenção') ||
            label.toLowerCase().includes('abstention') ||
            label.toLowerCase().includes('null') ||
            label === 'Null' ||
            label === 'null') {
          // Tradução para inglês
          let translatedLabel = label;
          if (label.toLowerCase() === 'abstenção') translatedLabel = 'abstention';
          abstractionLabels.push(translatedLabel);
          abstractionData.push(value);
        }
      });
      
      // Adicionar null se existir no formato novo
      if (isNewFormat && 'null' in distribution && distribution.null > 0) {
        if (!abstractionLabels.includes('Null')) {
          abstractionLabels.push('Null');
          abstractionData.push(Number(distribution.null));
        }
      }
      
      console.log(`Debug - Abstraction labels:`, abstractionLabels)
      console.log(`Debug - Abstraction data:`, abstractionData)
      
      // Calcular percentagem total de null e abstenção
      const totalAbstentionNull = abstractionData.reduce((sum, value) => sum + value, 0);
      
      console.log(`Debug - Total abstention/null:`, totalAbstentionNull)
      
      // Atualizar o elemento HTML com a percentagem total
      this.$nextTick(() => {
        const totalElement = document.getElementById(`total-abstention-${exampleId}`);
        if (totalElement) {
          totalElement.textContent = `${totalAbstentionNull.toFixed(1)}%`;
        }
        const summaryElement = document.getElementById(`summary-abstention-${exampleId}`);
        if (summaryElement) {
          summaryElement.textContent = `${totalAbstentionNull.toFixed(1)}%`;
        }
      });
      
      // Ordenar labels e valores
      const sortedAbs = this.combineAndSort(abstractionLabels, abstractionData);
      abstractionLabels = sortedAbs.labels;
      abstractionData = sortedAbs.data;
      
      const refName = 'abstractionChart' + exampleId;
      const ctxArr = this.$refs[refName];
      const ctx = Array.isArray(ctxArr) ? ctxArr[0] : ctxArr;
      if (!ctx) return;
      if (this.abstractionCharts[exampleId]) {
        this.abstractionCharts[exampleId].destroy();
      }
      this.abstractionCharts[exampleId] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: abstractionLabels,
          datasets: [{
            label: 'Abstention and Null (%)',
            data: abstractionData,
            backgroundColor: 'rgba(255, 99, 132, 0.8)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label(context) {
                  return context.parsed.y.toFixed(2) + '%'
                }
              }
            },
            title: {
              display: true,
              text: `Total non-voted: ${totalAbstentionNull.toFixed(1)}%`,
              font: {
                size: 14,
                weight: 'bold'
              },
              color: '#d32f2f',
              padding: {
                top: 50,
                bottom: 20
              }
            }
          },
          animation: {
            onComplete() {
              const ctx = this.ctx;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.font = '12px Arial';
              ctx.fillStyle = '#000';
              this.data.datasets.forEach(function(dataset) {
                for (let i = 0; i < dataset.data.length; i++) {
                  const model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                  ctx.fillText(dataset.data[i].toFixed(1) + '%', model.x, model.y + 15);
                }
              });
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              min: 0,
              max: 100,
              ticks: { callback: v => v + '%' }
            },
            yAxes: [{
              ticks: {
                beginAtZero: true,
                min: 0,
                max: 100,
                callback: v => v + '%'
              }
            }]
          }
        }
      });
    },

    async renderAllCharts() {
      for (const example of this.examples) {
        // Se houver filtros de perspectiva ativos, buscar dados específicos
        if (Object.keys(this.filters.perspectiveValues).length > 0) {
          const distribution = await this.fetchLabelDistribution(example.id)
          this.renderLabelsChart(example.id, distribution)
          this.renderAbstractionChart(example.id, distribution)
        } else {
          // Usar dados do exemplo se não houver filtros
          this.renderLabelsChart(example.id, example.label_distribution)
          this.renderAbstractionChart(example.id, example.label_distribution)
        }
      }
    },

    applyFilters() {
      console.log('Applying filters:', this.filters)
      console.log('Available categories:', this.categories)
      this.loading = true
      
      this.$nextTick(async () => {
        try {
          // Recarregar exemplos com filtros aplicados
          await this.fetchExamples()
          await this.fetchAllExamplesData()
          await this.fetchStatistics()
          
          // Re-renderizar gráficos
          this.$nextTick(async () => {
            await this.renderAllCharts()
          })
          
          console.log('Filters applied successfully')
        } catch (error) {
          console.error('Erro ao aplicar filtros:', error)
        } finally {
          this.loading = false
        }
      })
    },

    getPerspectiveFields(perspectiveId) {
      const perspective = this.perspectives.find(p => p.id === perspectiveId)
      console.log('Perspective:', perspective)
      return perspective && perspective.fields ? perspective.fields : []
    },

    async exportXLSX() {
      this.exportingXLSX = true
      try {
        await this.$nextTick(); // Garante que os gráficos estejam renderizados
        
        // Capturar imagens dos gráficos para incluir no XLSX
        const chartImages = {};
        const blankImg = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+X2ZkAAAAASUVORK5CYII=';
        
        for (const example of this.examples) {
          let labelsImg = null;
          let abstractionImg = null;
          
          if (this.labelsCharts[example.id]) {
            try {
              labelsImg = this.labelsCharts[example.id].toBase64Image();
            } catch (e) { 
              labelsImg = null; 
            }
          }
          
          if (this.abstractionCharts[example.id]) {
            try {
              abstractionImg = this.abstractionCharts[example.id].toBase64Image();
            } catch (e) { 
              abstractionImg = null; 
            }
          }
          
          if (!labelsImg) labelsImg = blankImg;
          if (!abstractionImg) abstractionImg = blankImg;
          
          chartImages[example.id] = {
            labels: labelsImg,
            abstraction: abstractionImg
          };
        }
        
        const params = this.buildExportParams();
        const url = `/v1/projects/${this.projectId}/statistics/export/xlsx?${params}`;
        const response = await this.$axios.post(url, { 
          chartImages, 
          screenExamples: this.screenExamples 
        }, { responseType: 'blob' });
        
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `estatisticas_por_texto_${this.projectId}_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(link.href)
        
        if (this.$toast && this.$toast.success) {
          this.$toast.success('Relatório XLSX exportado com sucesso!')
        }
      } catch (error) {
        console.error('Erro ao exportar XLSX:', error)
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro ao exportar relatório XLSX')
        }
      } finally {
        this.exportingXLSX = false
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

.export-btn {
  text-transform: uppercase;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  margin-right: 8px;
}

.v-expansion-panel-header {
  font-size: 18px;
  font-weight: 500;
}
</style> 