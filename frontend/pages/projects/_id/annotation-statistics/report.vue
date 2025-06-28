<template>
  <v-container fluid>
    <h1 class="text-h4 mb-4">Report Generator</h1>
    <div class="d-flex align-center justify-space-between mb-6">
      <div></div>
      <v-btn text aria-label="Return" @click="$router.back()">
        <v-icon left>{{ mdiArrowLeft }}</v-icon>
        Return
      </v-btn>
    </div>

    <v-card class="pa-8">
      <!-- EXAMPLES -->
      <v-row dense>
        <v-col cols="12" sm="6">
          <v-select
            v-model="filters.examples"
            :items="exampleOptions"
            label="Select Examples"
            multiple
            chips
            class="mb-2"
            item-text="text"
            item-value="value"
            :loading="loading.examples"
            :disabled="!exampleOptions.length"
          >
            <!-- Chip acts as delete button -->
            <template #selection="{ item }">
              <v-chip
                small
                close
                class="ma-1"
                @click="removeExample(item.value)"
                @click:close="removeExample(item.value)"
              >
                {{ item.text }}
              </v-chip>
            </template>
          </v-select>
        </v-col>
      </v-row>

      <!-- Versions & Perspectives -->
      <v-row dense class="mt-4">
        <v-col cols="12" sm="4">
          <v-select
            v-model="filters.versions"
            :items="versionOptions"
            label="Select Versions (union of all selected examples)"
            multiple
            chips
            class="mb-2"
            item-text="text"
            item-value="value"
            :loading="loading.versions"
            :disabled="!versionOptions.length"
          >
            <template #selection="{ item }">
              <v-chip
                small
                close
                class="ma-1"
                @click="removeVersion(item.value)"
                @click:close="removeVersion(item.value)"
              >
                {{ item.text }}
              </v-chip>
            </template>
          </v-select>
        </v-col>

        <v-col cols="12" sm="4">
          <v-select
            v-model="filters.perspectives"
            :items="perspectiveOptions"
            label="Select Perspectives"
            multiple
            chips
            class="mb-2"
            item-text="text"
            item-value="value"
            :loading="loading.perspectives"
            :disabled="!perspectiveOptions.length"
          >
            <template #selection="{ item }">
              <v-chip
                small
                close
                class="ma-1"
                @click="removePerspective(item.value)"
                @click:close="removePerspective(item.value)"
              >
                {{ item.text }}
              </v-chip>
            </template>
          </v-select>
        </v-col>

        <v-col cols="12" class="d-flex align-end">
          <v-btn text color="error" @click="clearFilters">CLEAR ALL FILTERS</v-btn>
        </v-col>
      </v-row>

      <!-- Generate report -->
      <v-btn color="primary" class="mt-4" @click="fetchReport" :disabled="!filters.examples.length">
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
              <td colspan="100%"
                 class="text-center">No data found. Try changing filters or generate anyway.</td>
            </tr>
            <tr
              v-for="row in reportData"
              :key="row.example + '-' + row.version + '-' + row.perspective"
            >
              <td>{{ row.exampleName }}</td>
              <td>{{ row.version }}</td>
              <td>{{ row.perspective }}</td>
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

const DEFAULT_THRESHOLD = 80

export default {
  name: 'AnnotationReportView',
  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      projectId: this.$route.params.id,
      threshold: DEFAULT_THRESHOLD,
      loading: { examples: false, versions: false, perspectives: false },
      filters: {
        examples: [], // array of example IDs
        versions: [], // array of version numbers (integers)
        perspectives: []
      },
      exampleOptions: [],
      versionOptions: [],
      perspectiveOptions: [],
      versionsByExample: {}, // { exId: [1,2,3] }
      reportData: [],
      tableHeaders: [],
      mdiArrowLeft
    }
  },

  watch: {
    'filters.examples'(val) {
      console.log('👀 Watch examples disparado:', val)
      this.filters.versions = []
      this.filters.perspectives = []
      this.versionOptions = []
      this.perspectiveOptions = []
      if (val.length) {
        console.log('🔄 Chamando fetchVersions...')
        this.fetchVersions()
      }
    },
    'filters.versions'(val) {
      console.log('👀 Watch versions disparado:', val)
      this.filters.perspectives = []
      this.perspectiveOptions = []
      if (val.length) this.fetchPerspectives()
    },
    versionOptions: {
      handler(newVal) {
        console.log('👀 Watch versionOptions disparado:', newVal)
        if (newVal.length > 0 && this.filters.examples.length > 0) {
          console.log('🔄 Chamando fetchReport automaticamente...')
          this.$nextTick(() => {
            this.fetchReport()
          })
        }
      },
      deep: true
    }
  },

  mounted() {
    this.fetchExamples()
  },

  methods: {
    /* ----------------------------------------------------------
     * Fetch EXAMPLES
     * -------------------------------------------------------- */
    async fetchExamples() {
      this.loading.examples = true
      try {
        const { items } = await this.$services.example.list(this.projectId, {})
        this.exampleOptions = items
          .filter(ex => ex.is_finished)
          .map(ex => ({
            text: ex.content || ex.text || ex.name || `Example ${ex.id}`,
            value: ex.id
          }))
      } finally {
        this.loading.examples = false
      }
    },

    /* ----------------------------------------------------------
     * Fetch VERSIONS – mostra a **união** de todas as versões dos examples
     * seleccionados. Só exibe depois de consultar todas as APIs.
     * -------------------------------------------------------- */
    async fetchVersions() {
      this.loading.versions = true
      this.versionsByExample = {}
      console.log('🔍 fetchVersions iniciado com examples:', this.filters.examples)
      try {
        // Dispara chamadas paralelas
        const calls = this.filters.examples.map(exId => {
          const url = `/api/dataset-version/${exId}/versions/`
          console.log(`📡 Fazendo request para: ${url}`)
          return this.$axios.$get(url).then(res => ({ exId, res }))
        })
        const results = await Promise.all(calls)
        console.log('📦 Resultados das chamadas:', results)

        const union = new Set()

        results.forEach(({ exId, res }) => {
          console.log(`📊 Processando resposta para exemplo ${exId}:`, res)
          const raw = res.versions || res || []
          const parsed = raw
            .map(v => {
              if (typeof v === 'number') return v
              if (typeof v === 'string') return parseInt(v, 10)
              if (v && typeof v === 'object' && 'version' in v) return Number(v.version)
              return NaN
            })
            .filter(n => !Number.isNaN(n))

          this.versionsByExample[exId] = parsed
          parsed.forEach(v => union.add(v))
        })

        this.versionOptions = Array.from(union)
          .sort((a, b) => a - b)
          .map(v => ({ text: `v${v}`, value: v }))
        console.log('✅ Versões finais:', this.versionOptions)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('❌ Erro ao obter versões:', err)
        console.error('❌ Detalhes do erro:', err.response?.data || err.message)
      } finally {
        this.loading.versions = false
      }
    },

    /* ----------------------------------------------------------
     * Fetch PERSPECTIVES for the selected examples & versions
     * -------------------------------------------------------- */
    async fetchPerspectives() {
      this.loading.perspectives = true
      console.log('🔍 fetchPerspectives iniciado com examples:', this.filters.examples, 'versions:', this.filters.versions)
      try {
        const set = new Set()
        for (const exId of this.filters.examples) {
          const url = `/api/dataset-version/${exId}/perspectives/`
          console.log(`📡 Fazendo request para: ${url}`)
          const response = await this.$axios.$get(url)
          console.log(`📊 Resposta para exemplo ${exId}:`, response)
          const { perspectives } = response
          this.filters.versions.forEach(v => {
            (perspectives[v] || []).forEach(u => set.add(u))
          })
        }
        this.perspectiveOptions = Array.from(set).map(u => ({ text: `User ${u}`, value: u }))
        console.log('✅ Perspectivas finais:', this.perspectiveOptions)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('❌ Erro ao obter perspectivas:', err)
        console.error('❌ Detalhes do erro:', err.response?.data || err.message)
      } finally {
        this.loading.perspectives = false
      }
    },

    /* ----------------------------------------------------------
     * REPORT GENERATION
     * -------------------------------------------------------- */
     async fetchReport() {
      console.log('🚀 fetchReport iniciado')
      const { examples, versions, perspectives } = this.filters
      console.log('📋 Filtros atuais:', { examples, versions, perspectives })
      if (!examples.length) return

      // Se não há versões selecionadas, usar todas as versões disponíveis
      const versionsToUse = versions.length ? versions : this.getAllAvailableVersions()
      console.log('📊 Versões a usar:', versionsToUse)
      if (!versionsToUse.length) return

       const rows = []

       for (const exId of examples) {
         for (const version of versionsToUse) {
           // Skip if the example does not have this version
           const hasVersion = this.versionsByExample[exId] && 
             this.versionsByExample[exId].includes(version)
           if (!hasVersion) continue

           let stats = {}
           try {
             const url = `/api/dataset-version/${exId}/${version}/stats/`
             console.log(`📡 Fazendo request para stats: ${url}`)
             stats = await this.$axios.$get(url)
             console.log(`📊 Stats para exemplo ${exId}, versão ${version}:`, stats)
           } catch (err) {
             // Preencher com zeros se falhar a obtenção
             console.warn(`⚠️ Sem dados para exemplo ${exId}, versão ${version}:`, err.response?.data || err.message)
           }

           // Se não houver estatísticas, preencher com zeros
           if (!stats || Object.keys(stats).length === 0) {
             stats = { total: 0, concordant: 0, discordant: 0 }
           }

           // Se não há perspectivas selecionadas, mostrar apenas os dados gerais
           if (perspectives.length) {
             perspectives.forEach(p =>
               rows.push({
                 example: exId,
                 exampleName: this.getExampleName(exId),
                 version,
                 perspective: p,
                 ...stats
               })
             )
           } else {
             rows.push({
               example: exId,
               exampleName: this.getExampleName(exId),
               version,
               perspective: 'All',
               ...stats
             })
           }
         }
       }

       // Mesmo que rows esteja vazio, criar uma estrutura padrão
       if (rows.length === 0 && examples.length && versionsToUse.length) {
         examples.forEach(exId => {
           versionsToUse.forEach(version => {
             const hasVersion = this.versionsByExample[exId] && 
               this.versionsByExample[exId].includes(version)
             if (!hasVersion) return
             if (perspectives.length) {
               perspectives.forEach(p =>
                 rows.push({
                   example: exId,
                   exampleName: this.getExampleName(exId),
                   version,
                   perspective: p,
                   total: 0,
                   concordant: 0,
                   discordant: 0
                 })
               )
             } else {
               rows.push({
                 example: exId,
                 exampleName: this.getExampleName(exId),
                 version,
                 perspective: 'All',
                 total: 0,
                 concordant: 0,
                 discordant: 0
               })
             }
           })
         })
       }

       this.tableHeaders = Object.keys(rows[0] || {}).filter(
         h => !['example', 'exampleName', 'version', 'perspective'].includes(h)
       )
       this.reportData = rows
       console.log('✅ Relatório gerado com sucesso!')
       console.log('📊 Total de linhas:', rows.length)
       console.log('📋 Headers da tabela:', this.tableHeaders)
     },

    /* ----------------------------------------------------------
     * HELPER: Get all available versions from selected examples
     * -------------------------------------------------------- */
    getAllAvailableVersions() {
      const allVersions = new Set()
      this.filters.examples.forEach(exId => {
        if (this.versionsByExample[exId]) {
          this.versionsByExample[exId].forEach(v => allVersions.add(v))
        }
      })
      return Array.from(allVersions).sort((a, b) => a - b)
    },

    /* ----------------------------------------------------------
     * CHIP REMOVERS
     * -------------------------------------------------------- */
    removeExample(val) {
      this.filters.examples = this.filters.examples.filter(v => v !== val)
      this.filters.versions = []
      this.filters.perspectives = []
      this.versionOptions = []
      this.perspectiveOptions = []
    },
    removeVersion(val) {
      this.filters.versions = this.filters.versions.filter(v => v !== val)
      this.filters.perspectives = []
      this.perspectiveOptions = []
    },
    removePerspective(val) {
      this.filters.perspectives = this.filters.perspectives.filter(v => v !== val)
    },

    /* ----------------------------------------------------------
     * HELPERS
     * -------------------------------------------------------- */
    getExampleName(id) {
      const found = this.exampleOptions.find(o => o.value === id)
      return found ? found.text : `Example ${id}`
    },
    clearFilters() {
      this.filters = { examples: [], versions: [], perspectives: [] }
      this.versionOptions = []
      this.perspectiveOptions = []
      this.versionsByExample = {}
      this.reportData = []
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
