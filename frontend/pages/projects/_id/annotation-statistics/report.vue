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
      <!-- Filtros principais em grid -->
      <div class="report-filters-grid mb-6">
        <!-- Examples -->
        <div class="filter-block">
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
        </div>
        <!-- Labels e Status -->
        <div class="filter-block">
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
        </div>
        <!-- Date Interval -->
        <div class="filter-block">
          <h2 class="text-h6 mb-4 primary--text">Date Interval</h2>
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
        </div>
      </div>

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
        <div v-if="!reportGenerated">
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
                    <tr v-for="(row, idx) in rows" :key="idx">
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

// Função debounce helper
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

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
      filteredPerspectiveUsers: [],
      reportGenerated: false,
    }
  },
  computed: {
    finalizedExamplesCount() {
      return this.exampleOptions.length;
    },
    
    activeFiltersCount() {
      let count = 0;
      
      // Contar filtros de array
      ['examples', 'versions', 'category'].forEach(key => {
        if (this.filters[key] && Array.isArray(this.filters[key])) {
          count += this.filters[key].length;
        }
      });
      
      // Contar filtros simples
      if (this.filters.status !== null && this.filters.status !== undefined) count += 1;
      if (this.filters.startDate) count += 1;
      if (this.filters.endDate) count += 1;
      
      // Contar filtros de perspectiva
      if (this.filters.perspectiveValues && typeof this.filters.perspectiveValues === 'object') {
        Object.values(this.filters.perspectiveValues).forEach(val => {
          if (val && val !== '') count += 1;
        });
      }
      
      return count;
    },
    
    hasActiveFilters() {
      return this.activeFiltersCount > 0;
    },
    
    // Verificar se há filtros de perspectiva ativos
    hasActivePerspectiveFilters() {
      return Object.values(this.filters.perspectiveValues || {})
        .some(val => val && val !== '');
    }
  },
  watch: {
    'filters.examples'(newVal, oldVal) {
      // Só resetar se realmente mudou
      if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
        this.filters.versions = [];
        this.versionOptions = [];
        if (this.filters.examples.length) {
          this.fetchVersions();
        }
      }
    },
    
    'filters.versions'() {
      if (this.filters.versions.length) {
        this.fetchPerspectives();
      }
    },
    
    'filters.perspectiveValues': {
      deep: true,
      handler: debounce(async function(newVal, oldVal) {
        // Verificar se realmente mudou
        if (JSON.stringify(newVal) === JSON.stringify(oldVal)) return;
        
        // Se tem filtros ativos, buscar usuários filtrados
        if (this.hasActivePerspectiveFilters) {
          await this.fetchFilteredPerspectiveUsers();
          
          // Log para debug
          if (this.filteredPerspectiveUsers.length > 0) {
            console.log('Usuários filtrados por perspectiva:', 
              this.filteredPerspectiveUsers.map(u => ({
                id: u.id,
                username: u.username,
                perspective: u.perspective
              }))
            );
          } else {
            console.log('Nenhum usuário encontrado com os filtros de perspectiva selecionados');
          }
        } else {
          // Limpar se não há filtros
          this.filteredPerspectiveUsers = [];
        }
      }, 500) // Debounce de 500ms para evitar muitas chamadas
    },
    
    // Watch para atualizar o relatório automaticamente quando mudam filtros importantes
    'filters.startDate'() {
      if (this.reportData && Object.keys(this.reportData).length > 0) {
        // Só regenerar se já tem dados
        this.debouncedFetchReport();
      }
    },
    
    'filters.endDate'() {
      if (this.reportData && Object.keys(this.reportData).length > 0) {
        this.debouncedFetchReport();
      }
    },
    
    'filters.category': {
      deep: true,
      handler() {
        if (this.reportData && Object.keys(this.reportData).length > 0) {
          this.debouncedFetchReport();
        }
      }
    }
  },
  created() {
    // Criar versão debounced do fetchReport
    this.debouncedFetchReport = debounce(this.fetchReport, 1000);
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
            return { id, res }
          })
        )
        const results = await Promise.all(calls)
        const versionOptions = []

        for (const { id, res } of results) {
          const raw = Array.isArray(res.versions) ? res.versions : []
          const vals = raw.map(v => typeof v === 'number' ? v : v.version).filter(n => Number.isFinite(n))
          this.versionsByExample[id] = vals

          const exampleLabel = this.exampleOptions.find(o => o.value === id)?.text || `Example ${id}`
          if (vals.length) {
            versionOptions.push({ header: exampleLabel })
            vals.sort((a, b) => a - b).forEach(v => {
              versionOptions.push({ text: `Version ${v}`, value: `${id}:${v}` })
            })
          }
        }

        this.versionOptions = versionOptions
      } catch (e) {
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
      // Limpar dados anteriores
      this.reportData = {};
      this.voteStatsByExampleVersion = {};
      
      // Se há filtros de perspectiva, buscar usuários filtrados primeiro
      if (Object.keys(this.filters.perspectiveValues).some(
        k => this.filters.perspectiveValues[k])) {
        await this.fetchFilteredPerspectiveUsers();
        await this.$nextTick();
      }
      
      // Gerar o relatório uma única vez
      await this._generateReportCore();
      this.reportGenerated = true;
    },

    async _generateReportCore() {
      let { examples } = this.filters;
      const { versions } = this.filters;

      // Se nenhum exemplo for selecionado, usar todos os exemplos disponíveis
      if (!examples.length) {
        examples = this.exampleOptions.map(opt => opt.value);
        // Buscar versões para todos os exemplos
        await this.fetchVersionsForExamples(examples);
      }

      const projectId = this.$route.params.id;
      const versionsToUse = versions.length
        ? versions.map(v => {
            const [ex, ver] = v.split(":");
            return { ex: +ex, ver: +ver };
          })
        : Object.entries(this.versionsByExample).flatMap(([ex, vers]) =>
            vers.map(ver => ({ ex: +ex, ver }))
          );

      const groupedData = {};
      const allLabels = new Set();

      // Obter IDs dos usuários filtrados por perspectiva
      const allowedUserIds = new Set();
      const allowedUsernames = new Set();
      
      if (this.filteredPerspectiveUsers.length > 0) {
        this.filteredPerspectiveUsers.forEach(user => {
          if (user.id) allowedUserIds.add(user.id);
          if (user.username) allowedUsernames.add(user.username);
        });
      }

      for (const { ex, ver } of versionsToUse) {
        if (!this.versionsByExample[ex]?.includes(ver)) continue;

        try {
          // Buscar estatísticas
          const params = this.buildStatsParams();
          const stats = await this.$axios.$get(
            `/v1/projects/${projectId}/dataset-version/${ex}/${ver}/stats/`,
            { params }
          );

          // Buscar estatísticas de votação de usuários
          const votingStats = await this.fetchVotingUserStats(projectId, ex, ver, params);
          this.voteStatsByExampleVersion[`${ex}:${ver}`] = {
            total_users: votingStats.total_users,
            users_voted: votingStats.users_voted,
            users_not_voted: votingStats.users_not_voted,
            users_only_abstention: votingStats.users_only_abstention,
            totalVotes: votingStats.total_votes
          };

          // Processar votos e recalcular percentuais se necessário
          const processedData = this.processVotesAndCalculatePercentages(
            stats,
            allowedUserIds,
            allowedUsernames,
            votingStats // <-- passar votingStats aqui
          );

          // Só adicionar se houver votos após filtragem
          if (processedData.totalVotes > 0 || !this.hasActivePerspectiveFilters) {
            const exampleName = this.getExampleName(ex);
            if (!groupedData[exampleName]) groupedData[exampleName] = {};
            if (!groupedData[exampleName][ver]) groupedData[exampleName][ver] = [];

            // Coletar labels únicos
            Object.keys(processedData.percentLabels).forEach(k => {
              if (k.startsWith('label_')) allLabels.add(k);
            });

            // Criar linha de dados
            const rowData = this.createRowData(
              ex,
              ver,
              processedData,
              votingStats
            );

            groupedData[exampleName][ver].push(rowData);
          }
        } catch (error) {
          console.error(`Erro ao buscar dados para exemplo ${ex}, versão ${ver}:`, error);
        }
      }

      // Configurar headers e dados finais
      this.configureTableHeaders();
      this.reportData = groupedData;
    },

    processVotesAndCalculatePercentages(stats, allowedUserIds, allowedUsernames, votingStats) {
          let filteredVotes = stats.votes || [];
      const hasUserFilter = allowedUserIds.size > 0 || allowedUsernames.size > 0;

      // Filtrar por data se necessário
      if (this.filters.startDate || this.filters.endDate) {
        filteredVotes = this.filterVotesByDate(filteredVotes);
      }

      // Filtrar por usuários permitidos (perspectiva)
      if (hasUserFilter) {
            filteredVotes = filteredVotes.filter(vote => {
          // Verificar por ID ou username
          return (vote.user && allowedUserIds.has(vote.user)) ||
                 (vote.user_id && allowedUserIds.has(vote.user_id)) ||
                 (vote.username && allowedUsernames.has(vote.username));
        });
      }

      // Separar votos válidos e abstenções
          const labelCounts = {};
      let nullCount = 0;
      const validVotes = filteredVotes.filter(
          vote => vote.label !== null && vote.label !== undefined);
      const totalVotes = validVotes.length; // Só votos válidos contam para percentuais

            filteredVotes.forEach(vote => {
        if (vote.label === null || vote.label === undefined) {
          nullCount++;
        } else {
              const labelKey = `label_${vote.label}`;
              labelCounts[labelKey] = (labelCounts[labelKey] || 0) + 1;
          }
      });

      // Calcular percentuais
          const percentLabels = {};
      Object.entries(labelCounts).forEach(([key, count]) => {
        percentLabels[key] = totalVotes > 0 
          ? `${((count / totalVotes) * 100).toFixed(2)}%` 
          : '0%';
      });
      // Adicionar percentual de abstenção (em relação ao total de usuários do projeto)
      const abstentionPercent = votingStats && votingStats.total_users > 0
        ? `${((nullCount / votingStats.total_users) * 100).toFixed(2)}%`
        : '0%';

      return {
        totalVotes,
        percentLabels,
        abstentionPercent,
        filteredVotes,
        labelCounts
      };
    },

    filterVotesByDate(votes) {
      if (!votes || !votes.length) return votes;

      const start = this.filters.startDate ? new Date(this.filters.startDate) : null;
      const end = this.filters.endDate ? new Date(this.filters.endDate) : null;

      return votes.filter(vote => {
        if (!vote.created_at) return true;
        const voteDate = new Date(vote.created_at);
        if (start && voteDate < start) return false;
        if (end && voteDate > end) return false;
        return true;
      });
    },

    buildStatsParams() {
      const params = {};
      
      // Não enviar filtros de perspectiva para o backend nas estatísticas gerais
      // Vamos filtrar localmente
      
      if (this.filters.startDate) params.start_date = this.filters.startDate;
      if (this.filters.endDate) params.end_date = this.filters.endDate;
      
      return params;
    },

    async fetchVotingUserStats(projectId, exampleId, version, baseParams) {
      try {
        // Para voting-user-stats, não enviamos filtros de perspectiva
        const params = { ...baseParams };
        Object.keys(params).forEach(key => {
          if (key.startsWith('perspective_')) {
            delete params[key];
          }
        });

        const stats = await this.$axios.$get(
          `/v1/projects/${projectId}/dataset-version/${exampleId}/${version}/voting-user-stats/`,
          { params }
        );
        
        return stats;
      } catch (error) {
        console.error('Erro ao buscar voting-user-stats:', error);
        return {};
      }
    },

    createRowData(exampleId, version, processedData, votingStats) {
      // Dados de perspectiva
      const perspectiveData = {};
      this.perspectiveFields.forEach(field => {
        if (this.filters.perspectiveValues[field.id]) {
          perspectiveData[field.name] = this.filters.perspectiveValues[field.id];
        }
      });

      // Dados de labels: garantir todos os headers de label presentes
      const labelData = {};
      let labelHeaders = [];
      if (this.filters.category && this.filters.category.length > 0) {
        labelHeaders = this.categoryOptions
          .filter(opt => this.filters.category.includes(opt.value))
          .map(opt => String(opt.text));
      } else {
        labelHeaders = this.categoryOptions.map(opt => String(opt.text));
      }
      labelHeaders.forEach(labelName => {
        // Se não existe, preencher com 0%
        labelData[labelName] = processedData.percentLabels[`label_${labelName}`] || '0%';
      });

      // Status se aplicável
      const statusData = {};
      if (this.filters.status !== null && this.filters.status !== undefined) {
        const statusOpt = this.statusOptions.find(opt => opt.value === this.filters.status);
        statusData.Status = statusOpt ? statusOpt.text : this.filters.status;
      }

      // Datas se aplicável
      const dateData = {};
      if (this.filters.startDate) dateData['Begin Date'] = this.filters.startDate;
      if (this.filters.endDate) dateData['End Date'] = this.filters.endDate;

      // Calcular percentual de "não votou" (null)
      let nullPercent = '0%';
      if (votingStats.total_users > 0) {
        const usersNotVoted = votingStats.users_not_voted || 0;
        nullPercent = `${((usersNotVoted / votingStats.total_users) * 100).toFixed(2)}%`;
      }

      return {
        example: exampleId,
        version,
        ...perspectiveData,
        ...labelData,
        ...statusData,
        ...dateData,
        abstention: processedData.abstentionPercent,
        null: nullPercent,
        // Metadados para ajudar no processamento
        _meta: {
          votes: processedData.filteredVotes,
          totalVotes: processedData.totalVotes,
          votingStats
        }
      };
    },

    configureTableHeaders() {
      // Campos de perspectiva filtrados
      const perspectiveHeaders = [];
      Object.entries(this.filters.perspectiveValues).forEach(([fieldId, value]) => {
        if (value) {
          const field = this.perspectiveFields.find(f => String(f.id) === String(fieldId));
          if (field) {
            perspectiveHeaders.push(field.name);
          }
        }
      });

      // Garantir que todos os labels do filtro (ou todos do projeto) estejam presentes
      let labelHeaders = [];
      if (this.filters.category && this.filters.category.length > 0) {
        // Apenas os labels filtrados
        labelHeaders = this.categoryOptions
          .filter(opt => this.filters.category.includes(opt.value))
          .map(opt => String(opt.text));
      } else {
        // Todos os labels do projeto
        labelHeaders = this.categoryOptions.map(opt => String(opt.text));
      }

      // Ordenar labels alfabeticamente
      labelHeaders.sort((a, b) => a.localeCompare(b));

      // Montar headers finais
      this.tableHeaders = [
        ...perspectiveHeaders,
        ...labelHeaders,
        ...(this.filters.status !== null ? ['Status'] : []),
        ...(this.filters.startDate ? ['Begin Date'] : []),
        ...(this.filters.endDate ? ['End Date'] : []),
        'abstention',
        'X (no vote)'
      ];
    },

    // Métodos auxiliares
    getExampleName(exampleId) {
      return this.exampleOptions.find(o => o.value === exampleId)?.text || `Example ${exampleId}`;
    },

    async fetchVersionsForExamples(exampleIds) {
      const projectId = this.$route.params.id;
      const calls = exampleIds.map(id =>
        this.$axios.$get(`/v1/projects/${projectId}/dataset-version/${id}/versions/`)
          .then(res => ({ id, res }))
          .catch(() => ({ id, res: { versions: [] } }))
      );

      const results = await Promise.all(calls);
      this.versionsByExample = {};
      
      results.forEach(({ id, res }) => {
        const versions = Array.isArray(res.versions) ? res.versions : [];
        this.versionsByExample[id] = versions
          .map(v => typeof v === 'number' ? v : v.version)
          .filter(v => Number.isFinite(v));
      });
    },

    // Método melhorado para obter estatísticas de voto
    getVoteStats(rows) {
      if (!Array.isArray(rows) || !rows.length) {
        return {
          totalUsers: 0,
          usersVoted: 0,
          usersNotVoted: 0,
          usersOnlyAbstention: 0,
          totalVotes: 0
        };
      }

      const row = rows[0];
      if (row._meta && row._meta.votingStats) {
        const stats = row._meta.votingStats;
        return {
          totalUsers: stats.total_users || 0,
          usersVoted: stats.users_voted || 0,
          usersNotVoted: stats.users_not_voted || 0,
          usersOnlyAbstention: stats.users_only_abstention || 0,
          totalVotes: row._meta.totalVotes || 0
        };
      }

      // Fallback para formato antigo
      const key = `${row.example}:${row.version}`;
      if (this.voteStatsByExampleVersion[key]) {
        const stats = this.voteStatsByExampleVersion[key];
        return {
          totalUsers: stats.total_users || 0,
          usersVoted: stats.users_voted || 0,
          usersNotVoted: stats.users_not_voted || 0,
          usersOnlyAbstention: stats.users_only_abstention || 0,
          totalVotes: row.total || 0
        };
      }

      return {
        totalUsers: 0,
        usersVoted: 0,
        usersNotVoted: 0,
        usersOnlyAbstention: 0,
        totalVotes: 0
      };
    },

    // Obter usernames filtrados
    getFilteredUsernames(rows) {
      if (!Array.isArray(rows) || !rows.length) return [];
      
      const usernames = new Set();
      rows.forEach(row => {
        if (row._meta && row._meta.votes) {
          row._meta.votes.forEach(vote => {
            if (vote.user) usernames.add(vote.user);
          });
        }
      });
      
      return Array.from(usernames);
    },

    // Método melhorado para buscar usuários filtrados por perspectiva
    async fetchFilteredPerspectiveUsers() {
      // Limpar usuários anteriores
      this.filteredPerspectiveUsers = [];

      // Obter apenas campos com valores selecionados
      const activeFilters = Object.entries(this.filters.perspectiveValues)
        .filter(([_, value]) => value && value !== '');

      if (!this.projectPerspective || activeFilters.length === 0) {
        return;
      }

      const projectPerspectiveId = this.projectPerspective.id;

      try {
        if (activeFilters.length === 1) {
          // Caso simples: apenas um filtro
          const [fieldId, value] = activeFilters[0];
          const field = this.perspectiveFields.find(f => String(f.id) === String(fieldId));
          const fieldName = field ? field.name : fieldId;

          console.log('Buscando usuários com filtro único:', { fieldName, value });

          const response = await this.$axios.$get('/api/v1/users_with_perspective_value/', {
            params: {
              project_perspective_id: projectPerspectiveId,
              field_name: fieldName,
              value
            }
          });

          this.filteredPerspectiveUsers = this.normalizeUserResponse(response);
          console.log(`Usuários encontrados: ${this.filteredPerspectiveUsers.length}`);

        } else {
          // Múltiplos filtros: buscar cada um e fazer interseção
          console.log('Buscando usuários com múltiplos filtros:', activeFilters);
          
          const userSetPromises = activeFilters.map(async ([fieldId, value]) => {
            const field = this.perspectiveFields.find(f => String(f.id) === String(fieldId));
            const fieldName = field ? field.name : fieldId;

            const response = await this.$axios.$get('/api/v1/users_with_perspective_value/', {
              params: {
                project_perspective_id: projectPerspectiveId,
                field_name: fieldName,
                value
              }
            });

            const users = this.normalizeUserResponse(response);
            return {
              fieldName,
              value,
              users,
              userIds: new Set(users.map(u => u.id))
            };
          });

          const userSets = await Promise.all(userSetPromises);

          // Log detalhado de cada conjunto
          userSets.forEach(({ fieldName, value, users }) => {
            console.log(`Campo "${fieldName}" = "${value}": ${users.length} usuários`);
          });

          // Calcular interseção
          const intersection = this.calculateUserIntersection(userSets);
          
          console.log(`Interseção final: ${intersection.length} usuários`);
          console.log('Usuários na interseção:', intersection.map(u => u.username || u.id));

          this.filteredPerspectiveUsers = intersection;
        }
      } catch (error) {
        console.error('Erro ao buscar usuários filtrados:', error);
        this.filteredPerspectiveUsers = [];
      }
    },

    // Normalizar resposta da API de usuários
    normalizeUserResponse(response) {
      if (Array.isArray(response)) {
        return response;
      } else if (response && Array.isArray(response.users)) {
        return response.users;
      }
      return [];
    },

    // Calcular interseção de conjuntos de usuários
    calculateUserIntersection(userSets) {
      if (userSets.length === 0) return [];
      if (userSets.length === 1) return userSets[0].users;

      // Começar com os IDs do primeiro conjunto
      let intersectionIds = userSets[0].userIds;

      // Fazer interseção com cada conjunto subsequente
      for (let i = 1; i < userSets.length; i++) {
        intersectionIds = new Set(
          [...intersectionIds].filter(id => userSets[i].userIds.has(id))
        );
      }

      // Recuperar objetos de usuário completos da interseção
      const userMap = new Map();
      userSets.forEach(({ users }) => {
        users.forEach(user => {
          if (intersectionIds.has(user.id)) {
            userMap.set(user.id, user);
          }
        });
      });

      return Array.from(userMap.values());
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
      this.filteredPerspectiveUsers = []
    },

    getExampleTotalUsers(versions) {
      const firstVersionRows = Object.values(versions)[0];
      if (!Array.isArray(firstVersionRows) || !firstVersionRows.length) return 0;
      return this.getVoteStats(firstVersionRows).totalUsers;
    },

    formatPercent(val) {
      if (val === undefined || val === null || val === '' || val === '-' || val === 0 || val === '0' || val === '0.0') return '0%';
      if (typeof val === 'string' && val.endsWith('%')) return val;
      const num = Number(val);
      if (isNaN(num)) return '0%';
      return num.toFixed(1) + '%';
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
              .filter(text => text && !text.includes('Example'))
              .join(', ');
            if (versionNames) parts.push(`Versions: ${versionNames}`);
          }
          // Categories nomes
          if (this.filters.category && this.filters.category.length) {
            const catNames = this.categoryOptions
              .filter(opt => this.filters.category.includes(opt.value))
              .map(opt => opt.text)
              .join(', ');
            parts.push(`Labels: ${catNames}`);
          }
          // Status nome
          if (this.filters.status !== null && this.filters.status !== undefined) {
            const statusName = (this.statusOptions.find(
              opt => opt.value === this.filters.status) || {}).text || this.filters.status;
            parts.push(`Status: ${statusName}`);
          }
          if (this.filters.startDate) parts.push(`Start Date: ${this.filters.startDate}`);
          if (this.filters.endDate) parts.push(`End Date: ${this.filters.endDate}`);
          // Perspective Values nomes
          if (this.filters.perspectiveValues &&
             Object.keys(this.filters.perspectiveValues).length) {
            const pvParts = Object.entries(this.filters.perspectiveValues)
              .filter(([_, val]) => val && val !== '')
              .map(([fid, val]) => {
                const field = this.perspectiveFields.find(f => String(f.id) === String(fid));
                const label = field ? field.name : fid;
                return `${label}: ${val}`;
              });
            if (pvParts.length) parts.push(`Perspective Values: ${pvParts.join(' | ')}`);
          }
          filterDesc += parts.join(' | ');
        } else {
          filterDesc = 'No filters applied. Showing all perspectives and options.';
        }
        csv += `"${filterDesc}"\n\n`;
        
        // Para cada exemplo
        Object.entries(this.reportData).forEach(([exampleName, versions]) => {
          // Total de usuários por exemplo
          const totalUsers = this.getExampleTotalUsers(versions);
          csv += `"${exampleName}";"Total users: ${totalUsers}"\n`;
          Object.entries(versions).forEach(([version, rows]) => {
            // Cabeçalho de bloco
            csv += `"Version ${version}";"Users that voted: ${this.getVoteStats(rows).usersVoted}"\n`;
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
                .filter(text => text && !text.includes('Example'))
                .join(', ');
              if (versionNames) parts.push(`Versions: ${versionNames}`);
            }
            // Categories nomes
            if (this.filters.category && this.filters.category.length) {
              const catNames = this.categoryOptions
                .filter(opt => this.filters.category.includes(opt.value))
                .map(opt => opt.text)
                .join(', ');
              parts.push(`Labels: ${catNames}`);
            }
            // Status nome
            if (this.filters.status !== null && this.filters.status !== undefined) {
              const statusName = (this.statusOptions.find(
                opt => opt.value === this.filters.status) || {}).text || this.filters.status;
              parts.push(`Status: ${statusName}`);
            }
            if (this.filters.startDate) parts.push(`Start Date: ${this.filters.startDate}`);
            if (this.filters.endDate) parts.push(`End Date: ${this.filters.endDate}`);
            // Perspective Values nomes
            if (this.filters.perspectiveValues &&
               Object.keys(this.filters.perspectiveValues).length) {
              const pvParts = Object.entries(this.filters.perspectiveValues)
                .filter(([_, val]) => val && val !== '')
                .map(([fid, val]) => {
                  const field = this.perspectiveFields.find(f => String(f.id) === String(fid));
                  const label = field ? field.name : fid;
                  return `${label}: ${val}`;
                });
              if (pvParts.length) parts.push(`Perspective Values: ${pvParts.join(' | ')}`);
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
                  const isMax = this.isMaxLabelCell(h, row);
                  const bgColor = isMax ? 'background:#fff9c4;font-weight:bold;' : '';
                  table += `<td style="border:1px solid #ccc;padding:6px 8px;text-align:center;${bgColor}">${val}</td>`;
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
    }
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
.report-filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 24px;
  width: 100%;
}
.filter-block {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  padding: 24px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style>