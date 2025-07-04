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

      <!-- Botões -->
      <v-btn color="primary" class="mt-4" 
        :disabled="!filters.examples.length" @click="fetchReport" >
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
              <td v-for="header in tableHeaders" :key="header">
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
    async fetchReport() {
      const { examples, versions, perspective, perspectiveValues } = this.filters
      if (!examples.length) return

      const versionsToUse = versions.length
        ? versions.map(v => {
            const [ex, ver] = v.split(":")
            return { ex: +ex, ver: +ver }
          })
        : Object.entries(this.versionsByExample).flatMap(([ex, vers]) =>
            vers.map(ver => ({ ex: +ex, ver }))
          )

      const projectId = this.$route.params.id
      const rows = []
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
          rows.push({
            example: ex,
            exampleName: this.exampleOptions.find(o => o.value === ex)?.text,
            version: ver,
            perspective,
            ...stats
          })
        } catch {
          rows.push({
            example: ex,
            exampleName: this.exampleOptions.find(o => o.value === ex)?.text,
            version: ver,
            perspective,
            total: 0,
            concordant: 0,
            discordant: 0
          })
        }
      }

      this.reportData = rows
      this.tableHeaders = rows.length
        ? Object.keys(rows[0]).filter(h => !['example', 'exampleName', 'version', 'perspective'].includes(h))
        : []
    },
    clearFilters() {
      this.filters.examples = []
      this.filters.versions = []
      this.filters.perspectiveValues = {}
      this.versionOptions = []
      this.reportData = []
      this.tableHeaders = []
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
