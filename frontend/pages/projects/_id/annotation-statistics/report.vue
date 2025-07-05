<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">
      Report Generator
      <v-alert type="info" class="mb-0" :value="true">
        Please fill out the filters for more specific reports.
        <br>
        <strong>Total finalized datasets:</strong> {{ finalizedExamplesCount }}
      </v-alert>
    </h1>

    <div class="d-flex align-center justify-space-between mb-6">
      <div></div>
      <v-btn text aria-label="Return" @click="$router.back()">
        <v-icon left>{{ mdiArrowLeft }}</v-icon>
        Return
      </v-btn>
    </div>

    <v-card class="pa-8">
      <v-row dense class="mb-6">
        <!-- Examples -->
        <v-col cols="12" md="6">
          <v-card class="pa-4" outlined>
            <h2 class="text-h6 mb-4 primary--text">Examples</h2>
            <v-select
              v-model="filters.examples"
              :items="exampleOptions"
              label="Select Examples"
              multiple
              chips
              color="primary"
              class="mb-4"
              item-text="text"
              item-value="value"
              :loading="loading.examples"
              :disabled="!exampleOptions.length"
            />
            <v-select
              v-model="filters.versions"
              :items="versionOptions"
              label="Select Versions (por example)"
              multiple
              chips
              color="primary"
              class="mb-4"
              item-text="text"
              item-value="value"
              :loading="loading.versions"
              :disabled="false"
            />
          </v-card>
        </v-col>

        <!-- Perspective -->
        <v-col cols="12" md="6">
          <v-card class="pa-4" outlined>
            <h2 v-if="projectPerspective" class="text-h6 mb-4 primary--text" >
              Perspective: {{ projectPerspective.name }}
            </h2>
            <v-row dense>
              <template v-if="perspectiveFields && perspectiveFields.length">
                <template v-for="field in perspectiveFields">
                  <v-col :key="field.id" cols="12" sm="6">
                    <v-select
                      v-model="filters.perspectiveValues[field.id]"
                      :items="field.choices"
                      :label="field.name"
                      multiple
                      chips
                      clearable
                      color="primary"
                      class="mb-4"
                    />
                  </v-col>
                </template>
              </template>
            </v-row>
          </v-card>
        </v-col>
      </v-row>

      <!-- Filtros adicionais -->
      <v-row dense class="mb-6">
        <v-col cols="12" md="6">
          <v-card class="pa-4" outlined>
            <h2 class="text-h6 mb-4 primary--text">Labels e Status</h2>
            <v-select
              v-model="filters.category"
              :items="categoryOptions"
              label="Labels"
              multiple
              chips
              clearable
              color="primary"
              class="mb-4"
            />
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Status"
              clearable
              color="primary"
              class="mb-4"
            />
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card class="pa-4 pl-0" outlined>
            <h2 class="text-h6 mb-4 primary--text" style="padding-left: 16px;">Date Interval</h2>
            <div class="d-flex" style="gap: 24px;">
              <div style="flex:1;">
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
                      label="Begin Date"
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
              </div>
              <div style="flex:1;">
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
                    />
                  </template>
                  <v-date-picker
                    v-model="filters.endDate"
                    @input="filters.endDateMenu = false"
                  />
                </v-menu>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Botões -->
      <v-btn color="primary" class="mt-4" 
        @click="fetchReport" >
        GENERATE REPORT
      </v-btn>
      <v-btn color="error" text class="mt-2" @click="clearFilters">
        CLEAR ALL FILTERS
      </v-btn>

      <!-- Tabela principal -->
      <div class="mt-8">
        <v-simple-table>
          <thead>
            <tr>
              <th v-for="header in tableHeaders" :key="header">{{ header }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!reportData.length">
              <td colspan="100%" class="text-center">
                No data found. Try changing filters or generate anyway.
              </td>
            </tr>
            <tr
              v-for="row in reportData"
              :key="`${row.Example}-${row.Version}-${row.perspective}`"
            >
              <td v-for="header in tableHeaders" :key="header">{{ row[header] }}</td>
            </tr>
          </tbody>
        </v-simple-table>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'

export default {
  name: 'AnnotationReportView',
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      mdiArrowLeft,
      loading: {
        examples: false,
        versions: false,
        perspectives: false
      },
      filters: {
        examples: [],
        versions: [],
        perspective: null,
        perspectiveValues: {},
        category: [],
        startDate: null,
        endDate: null,
        startDateMenu: false,
        endDateMenu: false,
        status: null
      },
      exampleOptions: [],
      versionOptions: [],
      perspectives: [],
      perspectiveFields: [],
      versionsByExample: {},
      reportData: [],
      tableHeaders: [],
      projectPerspective: null,
      categoryOptions: [],
      statusOptions: [
        { text: 'All', value: null },
        { text: 'Resolved', value: 'true' },
        { text: 'Not resolved', value: 'false' }
      ]
    }
  },
  computed: {
    finalizedExamplesCount() {
      return this.exampleOptions.length
    }
  },
  watch: {
    'filters.examples'() {
      this.filters.versions = []
      this.versionOptions = []
      if (this.filters.examples.length) this.fetchVersions()
    },
    'filters.versions'() {
      if (this.filters.versions.length) this.fetchPerspectives()
    }
  },
  mounted() {
    this.fetchExamples()
    this.fetchPerspectives()
    this.fetchCategories()
  },
  methods: {
    async fetchExamples() {
      this.loading.examples = true
      try {
        const { items } = await this.$services.example.list(this.$route.params.id, {})
        this.exampleOptions = items
          .filter(ex => ex.is_finished)
          .map(ex => ({
            text: ex.name || ex.content || ex.title || ex.text || `Example ${ex.id}`,
            value: ex.id
          }))
      } finally {
        this.loading.examples = false
      }
    },
    async fetchVersions() {
      this.loading.versions = true
      this.versionsByExample = {}
      try {
        const exampleIds = this.filters.examples
        const projectId = this.$route.params.id
        const calls = exampleIds.map(id =>
          this.$axios.$get(`/v1/projects/${projectId}/dataset-version/${id}/versions/`).then(res => {
            console.log(`Versões recebidas para example ${id}:`, res)
            return { id, res }
          })
        )
        const results = await Promise.all(calls)
        const versionOptions = []

        for (const { id, res } of results) {
          const raw = Array.isArray(res.versions) ? res.versions : []
          const vals = raw.map(v => +v).filter(n => Number.isFinite(n))
          this.versionsByExample[id] = vals

          const exampleLabel = this.exampleOptions.find(o => o.value === id)?.text || `Example ${id}`
          if (vals.length) {
            versionOptions.push({ header: exampleLabel })
            vals.sort((a, b) => a - b).forEach(v => {
              versionOptions.push({ text: `Version ${v}`, value: `${id}:${v}` })
            })
          }
        }

        console.log('Objeto versionsByExample final:', this.versionsByExample)
        this.versionOptions = versionOptions
      } catch (e) {
        console.error('Erro ao buscar versões:', e)
        this.versionOptions = []
      } finally {
        this.loading.versions = false
      }
    },
    async fetchPerspectives() {
      this.loading.perspectives = true
      try {
        const response =
           await this.$repositories.perspective.getProjectPerspective(this.$route.params.id)
        if (response && response.perspective) {
          this.projectPerspective = response.perspective
          this.perspectiveFields = response.perspective.fields || []
          this.perspectives = [response.perspective]
        } else {
          this.perspectiveFields = []
          this.perspectives = []
        }
      } catch {
        this.perspectiveFields = []
        this.perspectives = []
      } finally {
        this.loading.perspectives = false
      }
    },
    async fetchCategories() {
      try {
        const response = await this.$services.categoryType.list(this.$route.params.id)
        this.categoryOptions = response.map(cat => ({
          text: cat.text || cat.name || cat.label || cat.id,
          value: cat.id
        }))
      } catch (error) {
        this.categoryOptions = []
      }
    },
    async fetchReport() {
      let { examples } = this.filters;
      const { versions, perspective, perspectiveValues } = this.filters;
      // Se nenhum exemplo for selecionado, usar todos os exemplos disponíveis
      if (!examples.length) {
        // Buscar todos os exemplos possíveis
        examples = this.exampleOptions.map(opt => opt.value);
        // Buscar as versões para todos os exemplos se ainda não estiverem carregadas
        const projectId = this.$route.params.id;
        const calls = examples.map(id =>
          this.$axios.$get(`/v1/projects/${projectId}/dataset-version/${id}/versions/`).then(res => {
            return { id, res };
          })
        );
        const results = await Promise.all(calls);
        this.versionsByExample = {};
        for (const { id, res } of results) {
          const raw = Array.isArray(res.versions) ? res.versions : [];
          const vals = raw.map(v => +v).filter(n => Number.isFinite(n));
          this.versionsByExample[id] = vals;
        }
      }

      const projectId = this.$route.params.id
      const versionsToUse = versions.length
        ? versions.map(v => {
            const [ex, ver] = v.split(":")
            return { ex: +ex, ver: +ver }
          })
        : Object.entries(this.versionsByExample).flatMap(([ex, vers]) =>
            vers.map(ver => ({ ex: +ex, ver }))
          )

      const rows = []
      let allPerspectiveFields = []
      let allLabels = new Set()
      for (const { ex, ver } of versionsToUse) {
        if (!this.versionsByExample[ex]?.includes(ver)) continue
        let stats = {}
        try {
          const params = {}
          if (perspective) params.perspective = perspective
          if (perspectiveValues && Object.keys(perspectiveValues).length) {
            Object.entries(perspectiveValues).forEach(([k, val]) => {
              if (val) params[`perspective_${k}`] = val
            })
          }
          stats = await this.$axios.$get(`/v1/projects/${projectId}/dataset-version/${ex}/${ver}/stats/`, { params })
          // Coletar todos os campos de perspectiva e labels
          if (stats.perspective_fields) {
            allPerspectiveFields = 
              allPerspectiveFields.concat(Object.keys(stats.perspective_fields))
          }
          Object.keys(stats).forEach(k => {
            if (k.startsWith('label_')) allLabels.add(k)
          })
          // Preencher os campos de perspectiva na linha
          const perspectiveData = {}
          allPerspectiveFields.forEach(field => {
            perspectiveData[field] = stats.perspective_fields ? stats.perspective_fields[field] : ''
          })
          rows.push({
            example: ex,
            exampleName: this.exampleOptions.find(o => o.value === ex)?.text,
            version: ver,
            ...perspectiveData,
            ...stats
          })
        } catch {
          rows.push({
            example: ex,
            exampleName: this.exampleOptions.find(o => o.value === ex)?.text,
            version: ver,
            total: 0,
            concordant: 0,
            discordant: 0
          })
        }
      }
      // Remover duplicatas dos campos de perspectiva
      allPerspectiveFields = [...new Set(allPerspectiveFields)]
      allLabels = Array.from(allLabels)
      // Determinar os campos de perspectiva filtrados
      const filteredPerspectiveFields = 
        Object.keys(perspectiveValues).filter(k => perspectiveValues[k])
      // Mapear ids para nomes amigáveis
      const perspectiveFieldHeaders = filteredPerspectiveFields.map(id => {
        const field = this.perspectiveFields.find(f => String(f.id) === String(id))
        return field ? field.name : id
      })
      // Determinar labels a exibir: todos ou apenas os escolhidos
      let labelHeaders = allLabels;
      if (this.filters.category && this.filters.category.length > 0) {
        const selectedCats = 
          this.categoryOptions.filter(opt => this.filters.category.includes(opt.value));
        const selectedTexts = selectedCats.map(opt => String(opt.text).toLowerCase().trim());
        labelHeaders = allLabels.filter(lab => {
          const labelSuffix = lab.replace(/^label_/, '').toLowerCase().trim();
          return selectedTexts.includes(labelSuffix);
        });
        // Se não encontrar nenhum, mostra todos como fallback
        if (labelHeaders.length === 0) labelHeaders = allLabels;
      }
      // Montar nomes amigáveis para os labels nas colunas
      const labelColumnNames = labelHeaders.map(lab => lab.replace(/^label_/, ''));
      const tableHeaders = [
        'Example',
        'Version',
        ...perspectiveFieldHeaders,
        ...labelColumnNames,
        ...(this.filters.status !== null ? ['Status'] : []),
        ...(this.filters.startDate ? ['Begin Date'] : []),
        ...(this.filters.endDate ? ['End Date'] : []),
        'abstention',
        'null'
      ]
      // Ordenar rows por exampleName
      rows.sort((a, b) => (a.exampleName || '').localeCompare(b.exampleName || ''))
      
      this.reportData = rows.map(row => {
        const perspectiveData = {}
        filteredPerspectiveFields.forEach(fieldId => {
          const field = this.perspectiveFields.find(f => String(f.id) === String(fieldId))
          let value = this.filters.perspectiveValues[fieldId]
          if (field && field.choices && Array.isArray(value)) {
            value = value.map(v => {
              const choice = field.choices.find(c => c.value === v || c.id === v)
              return choice ? (choice.text || choice.label || choice.value) : v
            }).join(', ')
          } else if (field && field.choices) {
            const choice = field.choices.find(c => c.value === value || c.id === value)
            value = choice ? (choice.text || choice.label || choice.value) : value
          }
          perspectiveData[field ? field.name : fieldId] = value
        })
        // Montar objeto de labels filtrados, usando nomes amigáveis nas colunas
        const labelData = {};
        labelHeaders.forEach((label) => {
          let val = row[label];
          if (!val || val === '0%' || val === 0) val = '-';
          const colName = label.replace(/^label_/, '');
          labelData[colName] = val;
        });
        // Estado e datas
        let statusValue = ''
        if (this.filters.status !== null && this.filters.status !== undefined) {
          const statusOpt = this.statusOptions.find(opt => opt.value === this.filters.status)
          statusValue = statusOpt ? statusOpt.text : this.filters.status
        }
        return {
          Example: row.exampleName,
          Version: row.version,
          ...perspectiveData,
          ...labelData,
          ...(this.filters.status !== null ? { Status: statusValue } : {}),
          ...(this.filters.startDate ? { 'Begin Date': this.filters.startDate } : {}),
          ...(this.filters.endDate ? { 'End Date': this.filters.endDate } : {}),
          abstention: row.abstention || '',
          null: row.null || ''
        }
      })
      this.tableHeaders = tableHeaders
    },
    clearFilters() {
      this.filters.examples = []
      this.filters.versions = []
      this.filters.perspectiveValues = {}
      this.versionOptions = []
      this.filters.category = []
      this.filters.startDate = null
      this.filters.endDate = null
      this.filters.startDateMenu = false
      this.filters.endDateMenu = false
      this.filters.status = null
    }
  }
}
</script>

<style scoped>
.v-expansion-panel-header {
  font-size: 18px;
  font-weight: 500;
}
</style>
