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
      <v-btn color="error" text class="mt-2" @click="clearFilters">
        CLEAR ALL FILTERS
      </v-btn>
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
            <div v-for="(rows, version) in versions" :key="version" class="mb-4">
              <h3 class="text-subtitle-1 mb-1">Version {{ version }}</h3>
        <v-simple-table>
          <thead>
            <tr>
              <th v-for="header in tableHeaders" :key="header">{{ header }}</th>
            </tr>
          </thead>
          <tbody>
                  <tr v-for="(row, idx) in rows" 
                    :key="idx">
              <td v-for="header in tableHeaders" :key="header"
                :class="isMaxLabelCell(header, row) ? 'highlight-label' : ''">
                      <template v-if="header === 'abstention' || header === 'null'">
                        {{ formatPercent(row[header]) }}
                      </template>
                      <template v-else>
                {{ row[header] }}
                      </template>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
            </div>
          </v-card>
        </div>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
import { APIMemberRepository } from '@/repositories/member/apiMemberRepository'

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
      projectMembers: [],
      exportingCSV: false,
      exportingPDF: false,
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
    this.fetchProjectMembers()
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
    async fetchProjectMembers() {
      try {
        const projectId = this.$route.params.id
        const repo = new APIMemberRepository(this.$axios)
        this.projectMembers = await repo.list(projectId)
      } catch (e) {
        this.projectMembers = []
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
        ...perspectiveFieldHeaders,
        ...labelColumnNames,
        ...(this.filters.status !== null ? ['Status'] : []),
        ...(this.filters.startDate ? ['Begin Date'] : []),
        ...(this.filters.endDate ? ['End Date'] : []),
        'abstention',
        'null'
      ]
      // Ordenar rows por exampleName
      rows.sort((a, b) => (a.exampleName || '').localeCompare(b.exampleName || ''));
      
      // Agrupar dados por exemplo e versão
      const groupedData = {};
      rows.forEach(row => {
        const exampleName = row.exampleName || row.example || '';
        const version = row.version;
        if (!groupedData[exampleName]) groupedData[exampleName] = {};
        if (!groupedData[exampleName][version]) groupedData[exampleName][version] = [];
        const perspectiveData = {};
        filteredPerspectiveFields.forEach(fieldId => {
          const field = this.perspectiveFields.find(f => String(f.id) === String(fieldId));
          let value = this.filters.perspectiveValues[fieldId];
          if (field && field.choices && Array.isArray(value)) {
            value = value.map(v => {
              const choice = field.choices.find(c => c.value === v || c.id === v);
              return choice ? (choice.text || choice.label || choice.value) : v;
            }).join(', ');
          } else if (field && field.choices) {
            const choice = field.choices.find(c => c.value === value || c.id === value);
            value = choice ? (choice.text || choice.label || choice.value) : value;
          }
          perspectiveData[field ? field.name : fieldId] = value;
        });
        const labelData = {};
        labelHeaders.forEach((label) => {
          let val = row[label];
          if (!val || val === '0%' || val === 0) val = '0%';
          const colName = label.replace(/^label_/, '');
          labelData[colName] = val;
        });
        let statusValue = '';
        if (this.filters.status !== null && this.filters.status !== undefined) {
          const statusOpt = this.statusOptions.find(opt => opt.value === this.filters.status);
          statusValue = statusOpt ? statusOpt.text : this.filters.status;
        }
        groupedData[exampleName][version].push({
          ...perspectiveData,
          ...labelData,
          ...(this.filters.status !== null ? { Status: statusValue } : {}),
          ...(this.filters.startDate ? { 'Begin Date': this.filters.startDate } : {}),
          ...(this.filters.endDate ? { 'End Date': this.filters.endDate } : {}),
          abstention: (row.abstention !== undefined && row.abstention !== null) ?
             row.abstention : 0,
          null: (row.null !== undefined && row.null !== null) ? row.null : 0
        });
      });
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
    getUserStats(rows) {
      // Retorna { totalUsers, votaram, absteveOuNull }
      const totalUsers = this.projectMembers.length
     
      const row = rows && rows.length ? rows[0] : null
      let voted = null;
      let abstained = null;
      let nulled = null;
      if (row) {
        // Se vierem campos específicos, usa
        if ('voted_users' in row) voted = row.voted_users
        if ('abstention_users' in row) abstained = row.abstention_users
        if ('null_users' in row) nulled = row.null_users
      }
      // Se não vierem, só mostra total de usuários
      return {
        totalUsers,
        voted: voted !== null ? voted : '-',
        abstained: abstained !== null ? abstained : '-',
        nulled: nulled !== null ? nulled : '-',
      }
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
        // Para cada exemplo
        Object.entries(this.reportData).forEach(([exampleName, versions]) => {
          Object.entries(versions).forEach(([version, rows]) => {
            // Cabeçalho de bloco
            csv += `"${exampleName}";"Version ${version}"
`;
            // Cabeçalho de colunas
            csv += headers.map(h => `"${h}"`).join(';') + '\n';
            // Dados
            rows.forEach(row => {
              csv += headers.map(h => {
                let val = row[h];
                if (h === 'abstention' || h === 'null') val = this.formatPercent(val);
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
      try {
        // Geração de HTML para PDF
        let html = '<html><head><title>Relatório de Anotação</title>' +
          '<style>body{font-family:sans-serif;}table{border-collapse:collapse;width:100%;margin-bottom:24px;}th,td{border:1px solid #ccc;padding:6px 8px;text-align:center;}th{background:#f5f5f5;}h2{color:#1976d2;}h3{color:#333;}</style>' +
          '</head><body>';
        Object.entries(this.reportData).forEach(([exampleName, versions]) => {
          html += `<h2>${exampleName}</h2>`;
          Object.entries(versions).forEach(([version, rows]) => {
            html += `<h3>Version ${version}</h3>`;
            html += '<table><thead><tr>';
            this.tableHeaders.forEach(h => { html += `<th>${h}</th>`; });
            html += '</tr></thead><tbody>';
            rows.forEach(row => {
              html += '<tr>';
              this.tableHeaders.forEach(h => {
                let val = row[h];
                if (h === 'abstention' || h === 'null') val = this.formatPercent(val);
                if (val === undefined || val === null) val = '';
                html += `<td>${val}</td>`;
                return null;
              });
              html += '</tr>';
            });
            html += '</tbody></table>';
          });
        });
        html += '</body></html>';
        // Abrir nova janela e imprimir
        const printWindow = window.open('', '', 'width=900,height=700');
        printWindow.document.write(html);
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        this.$toast && this.$toast.success && this.$toast.success('Relatório PDF gerado via impressão!');
      } catch (error) {
        console.error('Erro ao exportar PDF:', error);
        this.$toast && this.$toast.error && this.$toast.error('Erro ao exportar relatório PDF');
      } finally {
        this.exportingPDF = false;
      }
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
