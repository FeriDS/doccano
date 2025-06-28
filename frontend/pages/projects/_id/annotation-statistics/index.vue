<template>
  <v-container fluid>
    <h1 class="text-h4 mb-4">Estatísticas por Texto</h1>
    <v-alert
      type="info"
      class="mb-4"
      :value="true"
    >
      <strong>Nota:</strong> Apenas datasets finalizados 
      são exibidos nesta página.
      <br>
      <strong>Total de datasets finalizados:</strong> {{ examples.length }}
    </v-alert>

    <!-- Filtros -->
    <v-card class="mb-6">
      <v-card-title>
        <v-icon left>mdi-filter</v-icon>
        Filtros
        <v-chip
          v-if="hasActiveFilters"
          color="primary"
          small
          class="ml-2"
        >
          {{ activeFiltersCount }} filtro(s) ativo(s)
        </v-chip>
        <v-spacer />
        <v-switch
          v-model="useLocalFiltering"
          label="Filtro Local"
          class="ml-4"
        />
      </v-card-title>
      <v-card-text>
        <v-alert
          v-if="useLocalFiltering"
          type="warning"
          dense
          class="mb-4"
        >
          <strong>Filtro Local Ativo:</strong> 
          Os dados são filtrados no navegador. Use esta opção se os
           filtros da API não estiverem funcionando.
        </v-alert>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.perspective"
              :items="perspectives"
              item-text="name"
              item-value="id"
              label="Perspetiva"
              clearable
              @change="onPerspectiveChange"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.label"
              :items="categories"
              item-text="text"
              item-value="id"
              label="Categoria"
              clearable
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.resolved"
              :items="statusOptions"
              item-text="text"
              item-value="value"
              label="Status"
              clearable
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
                  label="Data Início"
                  prepend-icon="mdi-calendar"
                  readonly
                  v-bind="attrs"
                  clearable
                  v-on="on"
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
                  label="Data Fim"
                  prepend-icon="mdi-calendar"
                  readonly
                  v-bind="attrs"
                  clearable
                  v-on="on"
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
            >
              <v-icon left>mdi-filter-check</v-icon>
              Aplicar Filtros
            </v-btn>
          </v-col>
          <v-col cols="12" md="3">
            <v-btn
              outlined
              @click="clearFilters"
            >
              <v-icon left>mdi-filter-remove</v-icon>
              Limpar Filtros
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
              <h3 class="text-h6 mb-3">Distribuição de Labels</h3>
              <div class="total-percentage mb-2">
                <v-chip
                  color="blue"
                  text-color="white"
                  class="font-weight-bold"
                  :label="true"
                >
                  Total Labels: <span :id="'total-labels-' + example.id">0%</span>
                </v-chip>
              </div>
              <div style="min-height: 250px;">
                <canvas :ref="'labelsChart' + example.id"></canvas>
              </div>
            </v-col>
            <v-col cols="6">
              <h3 class="text-h6 mb-3">Abstenção e Null</h3>
              <div class="total-percentage mb-2">
                <v-chip
                  color="red"
                  text-color="white"
                  class="font-weight-bold"
                  :label="true"
                >
                  Total non-voted: <span :id="'total-abstention-' + example.id">0%</span>
                </v-chip>
              </div>
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
                      Total Labels Regulares: <span :id="'summary-labels-' + example.id">0%</span>
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
      perspectiveChoices: [],
      allExamplesData: [],
      expandedPanels: [],
      charts: {},
      labelsCharts: {},
      abstractionCharts: {},
      useLocalFiltering: false,
      allExamples: [] // Para armazenar todos os exemplos quando usar filtro local
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
             this.filters.label || 
             this.filters.resolved !== null ||
             Object.keys(this.filters.perspectiveValues).length > 0
    },
    activeFiltersCount() {
      let count = 0
      if (this.filters.startDate) count++
      if (this.filters.endDate) count++
      if (this.filters.perspective) count++
      if (this.filters.label) count++
      if (this.filters.resolved !== null) count++
      count += Object.keys(this.filters.perspectiveValues).length
      return count
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
        this.$nextTick(() => {
          this.renderAllCharts()
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
    this.renderAllCharts()
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
          
          // Aplicar filtros localmente
          this.examples = this.allExamples.filter(example => {
            // Filtro por data
            if (this.filters.startDate && example.created_at) {
              const exampleDate = new Date(example.created_at).toISOString().split('T')[0]
              if (exampleDate < this.filters.startDate) return false
            }
            if (this.filters.endDate && example.created_at) {
              const exampleDate = new Date(example.created_at).toISOString().split('T')[0]
              if (exampleDate > this.filters.endDate) return false
            }
            
            // Filtro por perspetiva (se aplicável)
            if (this.filters.perspective && example.perspective_id) {
              if (example.perspective_id !== this.filters.perspective) return false
            }
            
            // Filtro por categoria (se aplicável)
            if (this.filters.label) {
              let hasCategory = false;

              const selectedCategory = this.categories.find(
                cat => cat.id === this.filters.label || cat.text === this.filters.label
              );
              const selectedCategoryId = selectedCategory ?
               String(selectedCategory.id) : String(this.filters.label);
              const selectedCategoryText = selectedCategory ?
               String(selectedCategory.text) : String(this.filters.label);

              // LOGS PARA DEBUG
              console.log('Filtro categoria:', this.filters.label);
              console.log('selectedCategory:', selectedCategory);
              console.log('selectedCategoryId:', selectedCategoryId);
              console.log('selectedCategoryText:', selectedCategoryText);
              console.log('label_distribution:', example.label_distribution);
              console.log('labels:', example.labels);

              if (example.label_distribution) {
                hasCategory = Object.keys(example.label_distribution).some(categoryName => {
                  console.log('Comparando chave:', categoryName, 'com', selectedCategoryId, selectedCategoryText);
                  return (
                    String(categoryName) === selectedCategoryId ||
                    String(categoryName) === selectedCategoryText
                  );
                });
              }

              if (!hasCategory && example.labels && Array.isArray(example.labels)) {
                hasCategory = example.labels.some(label => {
                  const labelCategoryId = String(label.category_id || label.category);
                  console.log('Comparando label:', labelCategoryId, 'com', selectedCategoryId, selectedCategoryText);
                  return (
                    labelCategoryId === selectedCategoryId ||
                    labelCategoryId === selectedCategoryText
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
            
            return true
          })
        } else {
          // Filtro via API
          const params = {}
          
          if (this.filters.startDate && this.filters.startDate.trim()) {
            params.start_date = this.filters.startDate
          }
          if (this.filters.endDate && this.filters.endDate.trim()) {
            params.end_date = this.filters.endDate
          }
          if (this.filters.perspective) {
            params.perspective = this.filters.perspective
          }
          if (this.filters.label) {
            params.label = this.filters.label
          }
          if (this.filters.resolved !== null && this.filters.resolved !== undefined) {
            params.resolved = this.filters.resolved
          }

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
        if (this.filters.label) params.label = this.filters.label
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
                ctx.textBaseline = 'bottom';
                ctx.font = '12px Arial';
                ctx.fillStyle = '#000';
                
                this.data.datasets.forEach(function(dataset) {
                  for (let i = 0; i < dataset.data.length; i++) {
                    const model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                    ctx.fillText(dataset.data[i].toFixed(1) + '%', model.x, model.y - 5);
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
        perspectiveValues: {}
      }
      
      // Recarregar dados sem filtros
      this.applyFilters()
    },

    async exportToCSV() {
      try {
        const params = this.getExportParams()
        params.export_format = 'csv'
        const response = await this.$repositories.statistics.fetchAnnotationStatistics(
          this.projectId,
          params
        )
        
        // Create a download link
        const blob = new Blob([response], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `annotation-statistics-${this.projectId}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        this.$toast && this.$toast.success('CSV export successful!')
      } catch (error) {
        console.error('Error exporting to CSV:', error)
        this.$toast && this.$toast.error('Error exporting to CSV')
      }
    },

    async exportToPDF() {
      try {
        const params = this.getExportParams();
        params.export_format = 'pdf';

        // Get the chart image as base64
        const chart = this.$refs.labelDistChart;
        let chartImage = null;
        if (chart) {
          chartImage = chart.toDataURL('image/png');
        }
        params.chartImage = chartImage;

        // Send as POST (since GET is not suitable for large payloads)
        const response = await this.$axios.$post(
          `/v1/projects/${this.projectId}/statistics/annotations`,
          params,
          { responseType: 'arraybuffer' }
        );

        // Download the PDF
        const blob = new Blob([response], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `annotation-statistics-${this.projectId}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        this.$toast && this.$toast.success('PDF export successful!');
      } catch (error) {
        console.error('Error exporting to PDF:', error);
        this.$toast && this.$toast.error('Error exporting to PDF');
      }
    },

    getExportParams() {
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
      return params
    },

    async fetchLabelDistribution(exampleId) {
      try {
        const response = await this.$axios.$get(`/v1/projects/${this.projectId}/discrepancies/${exampleId}/distribution`)
        return response
      } catch (error) {
        return {}
      }
    },

    renderLabelsChart(exampleId, distribution) {
      // Compatível com novo e antigo formato
      const isNewFormat = distribution && typeof distribution === 'object' && 'labels' in distribution;
      const allLabels = isNewFormat ? Object.keys(distribution.labels || {}) :
       Object.keys(distribution || {});
      const allData = isNewFormat ? Object.values(distribution.labels || {}).map(Number) : 
       Object.values(distribution || {}).map(Number);
      
      // Filtrar apenas labels regulares (excluir abstração e null)
      const regularLabels = [];
      const regularData = [];
      
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
            label: 'Distribuição de Labels (%)',
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
                size: 14,
                weight: 'bold'
              },
              color: '#1976d2'
            }
          },
          animation: {
            onComplete() {
              const ctx = this.ctx;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'bottom';
              ctx.font = '12px Arial';
              ctx.fillStyle = '#000';
              
              this.data.datasets.forEach(function(dataset) {
                for (let i = 0; i < dataset.data.length; i++) {
                  const model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                  ctx.fillText(dataset.data[i].toFixed(1) + '%', model.x, model.y - 5);
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
      // Compatível com novo e antigo formato
      const isNewFormat = distribution && typeof distribution === 'object' && 'labels' in distribution;
      const allLabels = isNewFormat ? Object.keys(distribution.labels || 
      {}) : Object.keys(distribution || {});
      const allData = isNewFormat ? Object.values(distribution.labels ||
       {}).map(Number) : Object.values(distribution || {}).map(Number);
      
      // Filtrar apenas abstração e null
      const abstractionLabels = [];
      const abstractionData = [];
      
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
          abstractionLabels.push(label);
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
      
      // Calcular percentagem total de null e abstenção
      const totalAbstentionNull = abstractionData.reduce((sum, value) => sum + value, 0);
      
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
            label: 'Abstenção e Null (%)',
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
              color: '#d32f2f'
            }
          },
          animation: {
            onComplete() {
              const ctx = this.ctx;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'bottom';
              ctx.font = '12px Arial';
              ctx.fillStyle = '#000';
              
              this.data.datasets.forEach(function(dataset) {
                for (let i = 0; i < dataset.data.length; i++) {
                  const model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                  ctx.fillText(dataset.data[i].toFixed(1) + '%', model.x, model.y - 5);
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

    renderAllCharts() {
      this.examples.forEach((example) => {
        this.renderLabelsChart(example.id, example.label_distribution)
        this.renderAbstractionChart(example.id, example.label_distribution)
      })
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
          this.$nextTick(() => {
            this.renderAllCharts()
          })
          
          console.log('Filters applied successfully')
        } catch (error) {
          console.error('Erro ao aplicar filtros:', error)
        } finally {
          this.loading = false
        }
      })
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