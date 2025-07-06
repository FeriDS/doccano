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
      <div class="d-flex align-center justify-space-between">
        <div>
          <v-btn color="primary" class="mr-2" @click="fetchReport">
            GENERATE REPORT
          </v-btn>
          <v-btn color="error" text class="mt-2 mr-2" @click="clearFilters">
            CLEAR ALL FILTERS
          </v-btn>
          <v-chip
            v-if="hasActiveFilters"
            small
            color="grey lighten-3"
            text-color="primary"
            class="ml-1"
            style="font-weight: 600;"
          >
            <v-icon left small>mdi-filter</v-icon>
            {{ activeFiltersCount }} filter(s) selected
          </v-chip>
        </div>
        <div>
          <v-btn color="success" :loading="exportingCSV" class="mr-2" @click="exportReportCSV">
            <v-icon left>mdi-file-excel</v-icon>
            Exportar CSV
          </v-btn>
          <v-btn color="error" :loading="exportingPDF" @click="exportReportPDF">
            <v-icon left>mdi-file-pdf</v-icon>
            Exportar PDF
          </v-btn>
        </div>
      </div>

      <!-- Tabela principal -->
      <div class="mt-8">
        <div v-if="Object.keys(reportData).length === 0">
          <v-simple-table>
            <tbody>
              <tr>
                <td colspan="100%" class="text-center">
                  Select some filters or generate without filters.
                </td>
              </tr>
            </tbody>
          </v-simple-table>
        </div>
        <div v-else>
          <v-card v-for="(versions, exampleName) in reportData" 
            :key="exampleName" class="mb-8 pa-6">
            <h2 class="text-h6 mb-2 primary--text">{{ exampleName }}</h2>
            <!-- Total de usuários por exemplo -->
            <div class="mb-2 text-body-1">
              Total users: {{ getExampleTotalUsers(versions) }}
            </div>
            <div v-for="(rows, version) in versions" :key="version" class="mb-4">
              <div style="border: 1px solid #eee; 
                border-radius: 6px; padding: 12px 8px; margin-bottom: 8px;">
                <h3 class="text-subtitle-1 mb-1 font-weight-bold">Version {{ version }}</h3>
                <div v-if="rows && rows.length" class="d-flex mb-2" style="gap: 32px;">
                  <div class="text-body-1">
                    Users that voted: {{ getVoteStats(rows).usersVoted }}
                  </div>
                </div>
        <v-simple-table>
          <thead>
            <tr>
              <th v-for="header in tableHeaders" :key="header">
                {{ header === 'X (no vote)' ? 'X (no vote)' : 
                  (header === 'abstention' ? 'Abstention' : header) }}
              </th>
            </tr>
          </thead>
          <tbody>
                    <tr v-for="(row, idx) in rows" 
                      :key="idx">
                      <td v-for="header in tableHeaders" :key="header"
                        :class="isMaxLabelCell(header, row) ? 'highlight-label' : ''">
                        <template v-if="header === 'abstention' || header === 'X (no vote)'">
                          {{ formatPercent(row[header === 'X (no vote)' ? 'null' : header]) }}
                        </template>
                        <template v-else>
                {{ row[header] }}
                        </template>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
              </div>
            </div>
          </v-card>
        </div>
      </div>
      <div class="d-flex justify-end mt-8">
        <v-btn text aria-label="Return" @click="$router.back()">
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'

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
      reportData: {},
      tableHeaders: [],
      projectPerspective: null,
      categoryOptions: [],
      statusOptions: [
        { text: 'All', value: null },
        { text: 'Resolved', value: 'true' },
        { text: 'Not resolved', value: 'false' }
      ],
      exportingCSV: false,
      exportingPDF: false,
      voteStatsByExampleVersion: {},
    }
  },
  computed: {
    finalizedExamplesCount() {
      return this.exampleOptions.length
    },
    activeFiltersCount() {
      let count = 0;
      if (this.filters.examples && 
      Array.isArray(this.filters.examples)) 
      count += this.filters.examples.length;
      if (this.filters.versions && 
      Array.isArray(this.filters.versions)) 
      count += this.filters.versions.length;
      if (this.filters.category && 
      Array.isArray(this.filters.category)) 
      count += this.filters.category.length;
      if (this.filters.status !== null && this.filters.status !== undefined) count += 1;
      if (this.filters.startDate) count += 1;
      if (this.filters.endDate) count += 1;
      if (this.filters.perspectiveValues && typeof this.filters.perspectiveValues === 'object') {
        Object.values(this.filters.perspectiveValues).forEach(val => {
          if (Array.isArray(val)) count += val.length;
          else if (val) count += 1;
        });
      }
      return count;
    },
    hasActiveFilters() {
      return this.activeFiltersCount > 0;
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
      // Novo: objeto para armazenar estatísticas de votação por exemplo/versão
      this.voteStatsByExampleVersion = {};
      const groupedData = {};
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
          if (this.filters.startDate) params.start_date = this.filters.startDate;
          if (this.filters.endDate) params.end_date = this.filters.endDate;
          stats = await this.$axios.$get(`/v1/projects/${projectId}/dataset-version/${ex}/${ver}/stats/`, { params })

          // NOVO: buscar estatísticas de votação do backend
          let votingStats = {};
          try {
            votingStats = await this.$axios.$get(`/v1/projects/${projectId}/dataset-version/${ex}/${ver}/voting-user-stats/`, { params });
            console.log('votingStats', votingStats);
          } catch (e) {
            votingStats = {};
          }
          this.voteStatsByExampleVersion[`${ex}:${ver}`] = votingStats;

          // NOVO: Filtragem local dos votos por data e perspectiva, se votes estiver presente
          let filteredVotes = stats.votes || [];
          // Filtrar por data
          if (filteredVotes.length && (this.filters.startDate || this.filters.endDate)) {
            const start = this.filters.startDate ? new Date(this.filters.startDate) : null;
            const end = this.filters.endDate ? new Date(this.filters.endDate) : null;
            filteredVotes = filteredVotes.filter(vote => {
              const voteDate = new Date(vote.created_at);
              if (start && voteDate < start) return false;
              if (end && voteDate > end) return false;
              return true;
            });
          }
          // Filtrar por perspectiva
          if (filteredVotes.length && this.perspectiveFields 
            && Object.keys(this.filters.perspectiveValues).length > 0) {
            filteredVotes = filteredVotes.filter(vote => {
              const member = this.projectMembers.find(
                  u => u.username === vote.user || u.id === vote.user || u.id === vote.user_id);
              if (!member || !member.perspective) return false;
              // Checar todos os campos de perspectiva filtrados
              return Object.entries(this.filters.perspectiveValues).every(([fieldId, value]) => {
                if (!value) return true;
                const field = this.perspectiveFields.find(f => String(f.id) === String(fieldId));
                if (!field) return true;
                const memberValue = member.perspective[field.name] || member.perspective[fieldId];
                if (Array.isArray(value)) {
                  return value.includes(memberValue);
                }
                return memberValue === value;
              });
            });
          }
          // Se filtrou, recalcula os percentuais
          const labelCounts = {};
          const totalVotes = filteredVotes.length;
          if (filteredVotes.length) {
            filteredVotes.forEach(vote => {
              const labelKey = `label_${vote.label}`;
              labelCounts[labelKey] = (labelCounts[labelKey] || 0) + 1;
            });
          }
          // Percentuais recalculados
          const percentLabels = {};
          Object.keys(labelCounts).forEach(k => {
            percentLabels[k] = totalVotes > 0 ? `${((labelCounts[k] / totalVotes) * 100).toFixed(2)}%` : '0%';
          });
          // Substitui os percentuais originais pelos recalculados, se votes foi filtrado
          if (filteredVotes.length || (this.filters.startDate || this.filters.endDate)) {
            Object.keys(percentLabels).forEach(k => { stats[k] = percentLabels[k]; });
            // Zera labels não presentes
            Object.keys(stats).forEach(k => {
              if (k.startsWith('label_') && !(k in percentLabels)) stats[k] = '0%';
            });
            stats.total = totalVotes;
          }
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
          const labelData = {}
          const labelHeaders = Array.from(allLabels)
          labelHeaders.forEach((label) => {
            let val = stats[label];
            if (!val || val === '0%' || val === 0) val = '0%';
            const colName = label.replace(/^label_/, '');
            labelData[colName] = val;
          });
          let statusValue = '';
          if (this.filters.status !== null && this.filters.status !== undefined) {
            const statusOpt = this.statusOptions.find(opt => opt.value === this.filters.status);
            statusValue = statusOpt ? statusOpt.text : this.filters.status;
          }
          // Agrupamento e push devem acontecer aqui, onde ex e ver existem
          const exampleName = this.exampleOptions.find(o => o.value === ex)?.text || `Example ${ex}`;
          if (!groupedData[exampleName]) groupedData[exampleName] = {};
          if (!groupedData[exampleName][ver]) groupedData[exampleName][ver] = [];

          // Novo cálculo para null
          const voteStats = this.getVoteStats([{ example: ex, version: ver }]);
          let nullPercent = 0;
          if (voteStats.totalUsers > 0) {
            nullPercent = ((voteStats.totalUsers - voteStats.usersVoted) /
               voteStats.totalUsers) * 100;
          }

          let abstentionPercent = '0%';
          if (voteStats.totalUsers > 0 && stats.votes && Array.isArray(stats.votes)) {
            const totalAbstVotes = stats.votes.filter(v => v.label === null).length;
            abstentionPercent = ((totalAbstVotes / voteStats.totalUsers) * 100).toFixed(2) + '%';
          }

          groupedData[exampleName][ver].push({
            example: ex,
            version: ver,
            ...perspectiveData,
            ...labelData,
            ...(this.filters.status !== null ? { Status: statusValue } : {}),
            ...(this.filters.startDate ? { 'Begin Date': this.filters.startDate } : {}),
            ...(this.filters.endDate ? { 'End Date': this.filters.endDate } : {}),
            abstention: abstentionPercent,
            null: nullPercent.toFixed(2) + '%'
          });
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
      // Remover o label 'null' dos headers dinâmicos para evitar coluna duplicada
      labelHeaders = labelHeaders.filter(lab => lab.replace(/^label_/, '').toLowerCase() !== 'null');
      // Montar nomes amigáveis para os labels nas colunas
      const labelColumnNames = labelHeaders.map(lab => lab.replace(/^label_/, ''));
      const tableHeaders = [
        ...perspectiveFieldHeaders,
        ...labelColumnNames,
        ...(this.filters.status !== null ? ['Status'] : []),
        ...(this.filters.startDate ? ['Begin Date'] : []),
        ...(this.filters.endDate ? ['End Date'] : []),
        'abstention',
        'X (no vote)'
      ]
      // Ordenar rows por exampleName
      rows.sort((a, b) => (a.exampleName || '').localeCompare(b.exampleName || ''));
      
      this.reportData = groupedData;
      this.tableHeaders = tableHeaders;
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
    },
    getTotalLabels(rows) {
      // Soma os percentuais das labels regulares (exclui 'abstention' e 'null')
      if (!rows || !rows.length) return '0.0';
      const labelKeys = this.tableHeaders.filter(h => h !== 'abstention' && h !== 'null' && h !== 'Status' && h !== 'Begin Date' && h !== 'End Date');
      let total = 0;
      for (const row of rows) {
        for (const key of labelKeys) {
          let val = row[key];
          if (typeof val === 'string' && val.endsWith('%')) val = parseFloat(val);
          if (!isNaN(val) && val !== '-' && key !== 'abstention' && key !== 'null') total += Number(val);
        }
      }
      return total.toFixed(1);
    },
    getTotalAbstentionNull(rows) {
      // Soma os percentuais das colunas 'abstention' e 'null'
      if (!rows || !rows.length) return '0.0';
      let total = 0;
      for (const row of rows) {
        ['abstention', 'null'].forEach(key => {
          let val = row[key];
          if (typeof val === 'string' && val.endsWith('%')) val = parseFloat(val);
          if (!isNaN(val) && val !== '-') total += Number(val);
        });
      }
      return total.toFixed(1);
    },
    formatPercent(val) {
      if (val === undefined || val === null || val === '' || val === '-' || val === 0 || val === '0' || val === '0.0') return '0%';
      if (typeof val === 'string' && val.endsWith('%')) return val;
      const num = Number(val);
      if (isNaN(num)) return '0%';
      return num.toFixed(1) + '%';
    },
    buildExportParams() {
      const params = new URLSearchParams();
      if (this.filters.startDate) params.append('start_date', this.filters.startDate);
      if (this.filters.endDate) params.append('end_date', this.filters.endDate);
      if (this.filters.category && this.filters.category.length > 0) params.append('label', this.filters.category.join(','));
      if (this.filters.status !== null && this.filters.status !== undefined) params.append('resolved', this.filters.status);
      if (this.filters.perspective) params.append('perspective', this.filters.perspective);
      Object.entries(this.filters.perspectiveValues).forEach(([fieldId, value]) => {
        if (value) params.append(`perspective_${fieldId}`, value);
      });
      return params.toString();
    },
    exportReportCSV() {
      this.exportingCSV = true;
      try {
        // Geração de CSV a partir dos dados do frontend
        const headers = this.tableHeaders;
        let csv = '';
        // Descrição dos filtros
        let filterDesc = '';
        if (this.hasActiveFilters) {
          filterDesc = 'Filters applied: ';
          const parts = [];
          // Examples nomes
          if (this.filters.examples && this.filters.examples.length) {
            const exampleNames = this.exampleOptions
              .filter(opt => this.filters.examples.includes(opt.value))
              .map(opt => opt.text)
              .join(', ');
            parts.push(`Examples: ${exampleNames}`);
          }
          // Versions nomes
          if (this.filters.versions && this.filters.versions.length) {
            const versionNames = this.versionOptions
              .filter(opt => this.filters.versions.includes(opt.value))
              .map(opt => opt.text || opt.header)
              .join(', ');
            parts.push(`Versions: ${versionNames}`);
          }
          // Categories nomes
          if (this.filters.category && this.filters.category.length) {
            const catNames = this.categoryOptions
              .filter(opt => this.filters.category.includes(opt.value))
              .map(opt => opt.text)
              .join(', ');
            parts.push(`Categories: ${catNames}`);
          }
          // Status nome
          if (this.filters.status !== null && this.filters.status !== undefined) {
            const statusName = (this.statusOptions.find(
              opt => opt.value === this.filters.status) || {}).text || this.filters.status;
            parts.push(`Status: ${statusName}`);
          }
          if (this.filters.startDate) parts.push(`Start Date: ${this.filters.startDate}`);
          if (this.filters.endDate) parts.push(`End Date: ${this.filters.endDate}`);
          // Perspective nome
          if (this.filters.perspective) {
            const perspName = (this.perspectives.find(
              p => p.id === this.filters.perspective) || {}).name || this.filters.perspective;
            parts.push(`Perspective: ${perspName}`);
          }
          // Perspective Values nomes
          if (this.filters.perspectiveValues &&
             Object.keys(this.filters.perspectiveValues).length) {
            const pvParts = Object.entries(this.filters.perspectiveValues).map(([fid, val]) => {
              const field = this.perspectiveFields.find(f => String(f.id) === String(fid));
              const label = field ? field.name : fid;
              let valueLabel = val;
              if (field && field.choices && Array.isArray(val)) {
                valueLabel = val.map(v => {
                  const choice = field.choices.find(
                    c => c === v || (c.value !== undefined && c.value === v));
                  return choice && choice.text ? choice.text : v;
                }).join(', ');
              } else if (field && field.choices) {
                const choice = field.choices.find(
                  c => c === val || (c.value !== undefined && c.value === val));
                valueLabel = choice && choice.text ? choice.text : val;
              }
              return `${label}: ${valueLabel}`;
            });
            parts.push(`Perspective Values: ${pvParts.join(' | ')}`);
          }
          filterDesc += parts.join(' | ');
        } else {
          filterDesc = 'No filters applied. Showing all perspectives and options.';
        }
        csv += `"${filterDesc}"

`;
        // Para cada exemplo
        Object.entries(this.reportData).forEach(([exampleName, versions]) => {
          // Total de usuários por exemplo
          const totalUsers = this.getExampleTotalUsers(versions);
          csv += `"${exampleName}";"Total users: ${totalUsers}"
`;
          Object.entries(versions).forEach(([version, rows]) => {
            // Cabeçalho de bloco
            csv += `"Version ${version}";"Users that voted: ${this.getVoteStats(rows).usersVoted}"
`;
            // Cabeçalho de colunas (apenas uma vez por bloco)
            csv += headers.map(h => `"${h}"`).join(';') + '\n';
            // Dados (apenas uma vez por linha)
            rows.forEach(row => {
              csv += headers.map(h => {
                let val;
                if (h === 'X (no vote)') {
                  val = row.null;
                } else {
                  val = row[h];
                }
                if (h === 'abstention' || h === 'X (no vote)') val = this.formatPercent(val);
                if (val === undefined || val === null) val = '';
                const safeVal = String(val).replace(/"/g, '""');
                return `"${safeVal}"`;
              }).join(';') + '\n';
            });
            csv += '\n';
          });
        });
        // Download
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `relatorio_anotacao_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        this.$toast && this.$toast.success && this.$toast.success('Relatório CSV exportado com sucesso!');
      } catch (error) {
        console.error('Erro ao exportar CSV:', error);
        this.$toast && this.$toast.error && this.$toast.error('Erro ao exportar relatório CSV');
      } finally {
        this.exportingCSV = false;
      }
    },
    exportReportPDF() {
      this.exportingPDF = true;
      this.$nextTick(async () => {
        try {
          const container = document.createElement('div');
          container.style.width = '800px';
          container.style.padding = '16px';
          container.style.fontFamily = 'sans-serif';
          container.innerHTML = '';

          // Descrição dos filtros
          let filterDesc = '';
          if (this.hasActiveFilters) {
            filterDesc = '<div style="font-weight:bold;margin-bottom:12px;">Filters applied: ';
            const parts = [];
            // Examples nomes
            if (this.filters.examples && this.filters.examples.length) {
              const exampleNames = this.exampleOptions
                .filter(opt => this.filters.examples.includes(opt.value))
                .map(opt => opt.text)
                .join(', ');
              parts.push(`Examples: ${exampleNames}`);
            }
            // Versions nomes
            if (this.filters.versions && this.filters.versions.length) {
              const versionNames = this.versionOptions
                .filter(opt => this.filters.versions.includes(opt.value))
                .map(opt => opt.text || opt.header)
                .join(', ');
              parts.push(`Versions: ${versionNames}`);
            }
            // Categories nomes
            if (this.filters.category && this.filters.category.length) {
              const catNames = this.categoryOptions
                .filter(opt => this.filters.category.includes(opt.value))
                .map(opt => opt.text)
                .join(', ');
              parts.push(`Categories: ${catNames}`);
            }
            // Status nome
            if (this.filters.status !== null && this.filters.status !== undefined) {
              const statusName = (this.statusOptions.find(
                opt => opt.value === this.filters.status) || {}).text || this.filters.status;
              parts.push(`Status: ${statusName}`);
            }
            if (this.filters.startDate) parts.push(`Start Date: ${this.filters.startDate}`);
            if (this.filters.endDate) parts.push(`End Date: ${this.filters.endDate}`);
            // Perspective nome
            if (this.filters.perspective) {
              const perspName = (this.perspectives.find(
                  p => p.id === this.filters.perspective) || {}).name || this.filters.perspective;
              parts.push(`Perspective: ${perspName}`);
            }
            // Perspective Values nomes
            if (this.filters.perspectiveValues &&
               Object.keys(this.filters.perspectiveValues).length) {
              const pvParts = Object.entries(this.filters.perspectiveValues).map(([fid, val]) => {
                const field = this.perspectiveFields.find(f => String(f.id) === String(fid));
                const label = field ? field.name : fid;
                let valueLabel = val;
                if (field && field.choices && Array.isArray(val)) {
                  valueLabel = val.map(v => {
                    const choice = field.choices.find(
                      c => c === v || (c.value !== undefined && c.value === v));
                    return choice && choice.text ? choice.text : v;
                  }).join(', ');
                } else if (field && field.choices) {
                  const choice = field.choices.find(
                    c => c === val || (c.value !== undefined && c.value === val));
                  valueLabel = choice && choice.text ? choice.text : val;
                }
                return `${label}: ${valueLabel}`;
              });
              parts.push(`Perspective Values: ${pvParts.join(' | ')}`);
            }
            filterDesc += parts.join(' | ') + '</div>';
          } else {
            filterDesc = '<div style="font-weight:bold;margin-bottom:12px;">No filters applied. Showing all perspectives and options.</div>';
          }
          container.innerHTML += filterDesc;

          Object.entries(this.reportData).forEach(([exampleName, versions]) => {
            const totalUsers = this.getExampleTotalUsers(versions);
            container.innerHTML += `<h2 style="color:#1976d2;">${exampleName}</h2>`;
            container.innerHTML += `<div style="margin-bottom:6px;font-weight:bold;">Total users: ${totalUsers}</div>`;

            Object.entries(versions).forEach(([version, rows]) => {
              container.innerHTML += `<div style="border:1px solid #eee;border-radius:6px;padding:12px 8px;margin-bottom:16px;">`;
              container.innerHTML += `<h3 style="color:#333;">Version ${version}</h3>`;
              container.innerHTML += `<div style="margin-bottom:8px;font-weight:bold;">Users that voted: ${this.getVoteStats(rows).usersVoted}</div>`;

              // tabela
              let table = '<table style="border-collapse:collapse;width:100%;margin-top:12px;">';
              table += '<thead><tr>';
              this.tableHeaders.forEach(h => {
                table += `<th style="border:1px solid #ccc;padding:6px 8px;background:#f5f5f5;text-align:center;">${h}</th>`;
              });
              table += '</tr></thead><tbody>';

              rows.forEach(row => {
                table += '<tr>';
                this.tableHeaders.forEach(h => {
                  let val;
                  if (h === 'X (no vote)') {
                    val = row.null;
                  } else {
                    val = row[h];
                  }
                  if (h === 'abstention' || h === 'X (no vote)') val = this.formatPercent(val);
                  if (val === undefined || val === null) val = '';
                  table += `<td style="border:1px solid #ccc;padding:6px 8px;text-align:center;">${val}</td>`;
                });
                table += '</tr>';
              });

              table += '</tbody></table>';
              container.innerHTML += table;
              container.innerHTML += '</div>';
            });
          });

          document.body.appendChild(container);
          const canvas = await html2canvas(container, { scale: 2 });
          const imgData = canvas.toDataURL('image/png');

          // eslint-disable-next-line new-cap
          const pdf = new jsPDF('p', 'mm', 'a4');
          const pdfWidth = pdf.internal.pageSize.getWidth();
          const pdfHeight = pdf.internal.pageSize.getHeight();

          // Calcula as dimensões da imagem em mm
          const imgProps = pdf.getImageProperties(imgData);
          const imgWidth = pdfWidth;
          const imgHeight = (imgProps.height * imgWidth) / imgProps.width;

          let heightLeft = imgHeight;
          let position = 0;

          // Adiciona a primeira página
          pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);

          heightLeft -= pdfHeight;

          // Adiciona páginas extras se necessário
          while (heightLeft > 0) {
            position = heightLeft - imgHeight;
            pdf.addPage();
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pdfHeight;
          }

          pdf.save(`relatorio_anotacao_${new Date().toISOString().split('T')[0]}.pdf`);

          document.body.removeChild(container);

          this.$toast && this.$toast.success && this.$toast.success('Relatório PDF exportado com sucesso!');
        } catch (error) {
          console.error('Erro ao exportar PDF:', error);
          this.$toast && this.$toast.error && this.$toast.error('Erro ao exportar relatório PDF');
        } finally {
          this.exportingPDF = false;
        }
      });
    },
    // Retorna true se este header é o label de maior valor da linha
    isMaxLabelCell(header, row) {
      // Só aplica para colunas de label regular
      if (['abstention', 'null', 'Status', 'Begin Date', 'End Date'].includes(header)) return false;
      // Pega só os valores das colunas de label
      const labelKeys = this.tableHeaders.filter(h => !['abstention', 'null', 'Status', 'Begin Date', 'End Date'].includes(h));
      let max = -Infinity;
      let maxKey = null;
      labelKeys.forEach(h => {
        let val = row[h];
        if (typeof val === 'string' && val.endsWith('%')) val = parseFloat(val);
        if (!isNaN(val) && val > max) {
          max = val;
          maxKey = h;
        }
      });
      return header === maxKey && max > 0;
    },
    // Calcula estatísticas de votos/abstenção/null por versão
    getVoteStats(rows) {
    if (!rows || !rows.length)
      return {
        totalUsers: 0,
        usersVoted: 0,
        usersNotVoted: 0,
        usersOnlyAbstention: 0,
        totalVotes: 0
      };
    const row = rows[0];
    const key = row && row.example !== undefined && row.version !== undefined
      ? `${row.example}:${row.version}`
      : null;
    if (key && this.voteStatsByExampleVersion && this.voteStatsByExampleVersion[key]) {
      const stats = this.voteStatsByExampleVersion[key];
      return {
        totalUsers: stats.total_users || 0,
        usersVoted: stats.users_voted || 0,
        usersNotVoted: stats.users_not_voted || 0,
        usersOnlyAbstention: stats.users_only_abstention || 0,
        totalVotes: row.total || 0
      };
    }
    // fallback antigo
    return {
      totalUsers: 0,
      usersVoted: 0,
      usersNotVoted: 0,
      usersOnlyAbstention: 0,
      totalVotes: 0
    };
  },
    getExampleTotalUsers(versions) {
      const firstVersionRows = Object.values(versions)[0];
      if (!firstVersionRows || !firstVersionRows.length) return 0;
      return this.getVoteStats(firstVersionRows).totalUsers;
    },
    getAbstentionPercent(stats, voteStats) {
      // Lógica igual ao discrepancy_automatic.vue: soma dos valores de stats.abstencao
      if (stats && stats.abstencao && voteStats && voteStats.totalUsers > 0) {
        const totalAbst = Object.values(stats.abstencao).reduce((a, b) => a + Number(b), 0);
        return ((totalAbst / voteStats.totalUsers) * 100).toFixed(2) + '%';
      }
      return '0%';
    },
  }
}
</script>

<style scoped>
.v-expansion-panel-header {
  font-size: 18px;
  font-weight: 500;
}
td.highlight-label {
  background: #fff9c4;
  font-weight: bold;
}
</style>
