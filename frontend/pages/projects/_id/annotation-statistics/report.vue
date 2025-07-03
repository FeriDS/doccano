<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">
      Report Generator
      <v-alert
      type="info"
      class="mb-0"
      :value="true"
    >
      Please fill out the filters for more specific reports.<br>
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
      
      
      <!-- Filtros principais: Examples (esquerda) e Perspectiva (direita) -->
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
              label="Select Versions (union of all selected examples)"
              multiple
              chips
              color="primary"
              class="mb-4"
              item-text="text"
              item-value="value"
              :loading="loading.versions"
              :disabled="!versionOptions.length"
            />
            <v-btn color="error" text :disabled="false" class="mt-2" @click="clearFilters">
              CLEAR ALL FILTERS
            </v-btn>
          </v-card>
        </v-col>
        <!-- Perspectiva -->
        <v-col cols="12" md="6">
          <v-card class="pa-4" outlined>
            <h2 class="text-h6 mb-4 primary--text" v-if="projectPerspective">
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

      <!-- Generate report -->
      <v-btn
        color="primary"
        class="mt-4"
        @click="fetchReport"
        :disabled="!filters.examples.length"
      >
        GENERATE REPORT
      </v-btn>

      <!-- Results table -->
      <div class="mt-8">
        <v-simple-table>
          <thead>
            <tr>
              <th>Example</th>
              <th>Version</th>
              <th>Perspective</th>
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
              :key="`${row.example}-${row.version}-${row.perspective}`"
            >
              <td>{{ row.exampleName }}</td>
              <td>{{ row.version }}</td>
              <td>{{ row.perspective }}</td>
              <td
                v-for="header in tableHeaders"
                :key="header"
              >
                {{ row[header] }}
              </td>
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
        perspectiveValues: {}
      },
      exampleOptions: [],
      versionOptions: [],
      perspectives: [],
      perspectiveFields: [],
      versionsByExample: {},
      reportData: [],
      tableHeaders: [],
      projectPerspective: null
    }
  },
  computed: {
    finalizedExamplesCount() {
      return this.exampleOptions.length;
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
    },
    versionOptions: {
      handler(newVal) {
        if (newVal.length && this.filters.examples.length) this.fetchReport()
      },
      deep: true
    }
  },
  mounted() {
    this.fetchExamples()
    this.fetchPerspectives()
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
      const calls = this.filters.examples.map(id =>
        this.$axios.$get(`/api/dataset-version/${id}/versions/`).then(res => ({ id, res }))
      )
      const results = await Promise.all(calls)
      const union = new Set()
      for (const { id, res } of results) {
        const raw = res.versions || res || []
        const vals = raw
          .map(v => (typeof v === 'object' && 'version' in v ? +v.version : +v))
          .filter(n => !Number.isNaN(n))
        this.versionsByExample[id] = vals
        vals.forEach(v => union.add(v))
      }
      this.versionOptions = Array.from(union)
        .sort((a, b) => a - b)
        .map(v => ({ text: `v${v}`, value: v }))
      this.loading.versions = false
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
    async fetchReport() {
      const { examples, versions, perspective, perspectiveValues } = this.filters
      if (!examples.length) return
      const versionsToUse = versions.length
        ? versions
        : Object.values(this.versionsByExample).flat()
      const rows = []
      for (const ex of examples) {
        for (const v of versionsToUse) {
          if (!this.versionsByExample[ex]?.includes(v)) continue
          let stats = {}
          try {
            const params = {}
            if (perspective) params.perspective = perspective
            if (perspectiveValues && Object.keys(perspectiveValues).length) {
              Object.entries(perspectiveValues).forEach(([k, val]) => {
                if (val) params[`perspective_${k}`] = val
              })
            }
            stats = await this.$axios.$get(`/api/dataset-version/${ex}/${v}/stats/`, { params })
            rows.push({
              example: ex,
              exampleName: this.exampleOptions.find(o => o.value === ex)?.text,
              version: v,
              perspective,
              ...stats
            })
          } catch {
            rows.push({
              example: ex,
              exampleName: this.exampleOptions.find(o => o.value === ex)?.text,
              version: v,
              perspective,
              total: 0,
              concordant: 0,
              discordant: 0
            })
          }
        }
      }
      this.reportData = rows
      this.tableHeaders = rows.length
        ? Object.keys(rows[0]).filter(h => !['example', 'exampleName', 'version', 'perspective'].includes(h))
        : []
    },
    removeExample(val) {
      this.filters.examples = this.filters.examples.filter(x => x !== val)
    },
    removeVersion(val) {
      this.filters.versions = this.filters.versions.filter(x => x !== val)
    },
    clearFilters() {
      this.filters.examples = [];
      this.filters.versions = [];
      this.filters.perspectiveValues = {};
      this.versionOptions = [];
      this.reportData = [];
      this.tableHeaders = [];
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
