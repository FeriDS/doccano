<template>
  <v-container class="pa-5 mt-16">
    <v-card>
      <v-card-title>
        <h2>Votação de Regras</h2>
        <v-spacer></v-spacer>
        <v-select
          v-model="filterStatus"
          :items="filterOptions"
          label="Filtrar por Status"
          dense
          outlined
          hide-details
          class="mr-4"
          style="max-width: 200px;"
        ></v-select>
        <v-btn
          text
          aria-label="Voltar"
          @click="$router.back()"
        >
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </v-card-title>

      <v-row class="px-4 pb-2">
        <v-btn
          color="primary"
          class="text-capitalize"
          @click="$router.push(localePath(`/projects/${$route.params.id}/rules/create`))"
        >
          <v-icon left>{{ mdiPlus }}</v-icon>
          {{ $t('rules.create') }}
        </v-btn>
      </v-row>

      <v-card-text>
        <!-- Erro ao carregar -->
        <v-alert v-if="error" type="error" dense class="mb-4">
          {{ error }}
        </v-alert>

        <!-- Loading spinner -->
        <v-progress-circular v-if="loading" indeterminate class="ma-4" />

        <!-- Tabela de regras -->
        <v-data-table
          v-if="filteredRules.length"
          :headers="headers"
          :items="filteredRules"
          item-key="id"
          class="elevation-1 mt-4"
        >
          <!-- Coluna 'Regra' -->
          <template #[`item.rule.text`]="{ item }">
            {{ item.rule.text }}
          </template>

          <!-- Coluna 'Status' -->
          <template #[`item.status`]="{ item }">
            <v-chip :color="getStatusColor(item.is_open, item.user_has_voted)">
              {{ getStatusText(item.is_open, item.user_has_voted) }}
            </v-chip>
          </template>

          <!-- Coluna 'Seu Voto' -->
          <template #[`item.user_vote`]="{ item }">
            <template v-if="item.user_has_voted">
              <v-icon :color="item.vote === true ? 'success' : 'error'">
                {{ item.vote === true ? mdiCheck : mdiClose }}
              </v-icon>
              {{ item.vote === true ? 'Sim' : 'Não' }}
            </template>
            <template v-else>
              N/A
            </template>
          </template>

          <!-- Coluna 'Votos Sim' -->
          <template #[`item.votes_yes`]="{ item }">
            {{ item.votes_yes }}
          </template>

          <!-- Coluna 'Votos Não' -->
          <template #[`item.votes_no`]="{ item }">
            {{ item.votes_no }}
          </template>
          
          <!-- Coluna 'Ações' -->
          <template #[`item.action`]="{ item }">
            <v-btn
              v-if="item.is_open && !item.user_has_voted"
              icon
              color="success"
              @click="voteRule(item.id, true)"
            >
              👍
            </v-btn>
            <v-btn
              v-if="item.is_open && !item.user_has_voted"
              icon
              color="error"
              @click="voteRule(item.id, false)"
            >
              👎
            </v-btn>
            <v-btn
              v-if="item.is_open && isAdmin"
              icon
              small
              @click="closeVoting(item.id)"
            >
              <v-icon>{{ mdiLock }}</v-icon>
            </v-btn>
          </template>
        </v-data-table>

        <!-- Nenhuma regra -->
        <div v-if="!loading && !rules.length" class="text-gray-600 mt-4">
          Nenhuma regra encontrada para este projeto.
        </div>
      </v-card-text>
    </v-card>

    <!-- Snackbar de feedback -->
    <v-snackbar v-model="snackbar" top :color="snackbarColor" :timeout="3000">
      {{ snackbarMessage }}
    </v-snackbar>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiArrowLeft, mdiCheck, mdiClose, mdiLock, mdiPlus } from '@mdi/js'
import { useRuleVoting } from '~/composables/useRuleVoting'
import type { RuleDTO } from '@/repositories/rule/apiRuleRepository'

interface Data {
  rules: RuleDTO[]
  loading: boolean
  error: string
  snackbar: boolean
  snackbarMessage: string
  snackbarColor: 'success' | 'error'
  filterStatus: string
  filterOptions: string[]
  isAdmin: boolean
  mdiArrowLeft: string
  mdiCheck: string
  mdiClose: string
  mdiLock: string
  mdiPlus: string
}

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data(): Data {
    return {
      rules: [],
      loading: false,
      error: '',
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success',
      filterStatus: 'Todas',
      filterOptions: ['Todas', 'Abertas', 'Fechadas', 'Votadas', 'Não Votadas'],
      isAdmin: false, // Será preenchido no created
      mdiArrowLeft,
      mdiCheck,
      mdiClose,
      mdiLock,
      mdiPlus
    }
  },

  computed: {
    filteredRules(): RuleDTO[] {
      return this.rules.filter(rule => {
        if (this.filterStatus === 'Todas') {
          return true
        } else if (this.filterStatus === 'Abertas') {
          return rule.is_open
        } else if (this.filterStatus === 'Fechadas') {
          return !rule.is_open
        } else if (this.filterStatus === 'Votadas') {
          return rule.user_has_voted
        } else if (this.filterStatus === 'Não Votadas') {
          return !rule.user_has_voted
        }
        return true
      })
    },

    headers(): any[] {
      return [
        { text: 'Regra', value: 'rule.text' },
        { text: 'Status', value: 'status', sortable: false },
        { text: 'Seu Voto', value: 'user_vote', sortable: false },
        { text: 'Votos Sim', value: 'votes_yes' },
        { text: 'Votos Não', value: 'votes_no' },
        { text: 'Ações', value: 'action', sortable: false }
      ]
    }
  },

  watch: {
    filterStatus() {
      this.fetchRules() // Recarrega as regras ao mudar o filtro
    }
  },

  async created() {
    // Buscar o papel do usuário para definir isAdmin
    try {
      const userRole = await this.$repositories.member.fetchMyRole(this.$route.params.id)
      this.isAdmin = userRole.isProjectAdmin // Ajuste conforme a estrutura do seu objeto de role
    } catch (err) {
      console.error('Erro ao buscar o papel do usuário:', err)
      this.isAdmin = false
    }
    await this.fetchRules()
  },

  methods: {
    getStatusText(isOpen: boolean, userHasVoted: boolean): string {
      if (isOpen) {
        return userHasVoted ? 'Votada' : 'Aberta'
      } else {
        return 'Fechada'
      }
    },

    getStatusColor(isOpen: boolean, userHasVoted: boolean): string {
      if (isOpen) {
        return userHasVoted ? 'success' : 'info'
      } else {
        return 'red' // ou 'grey' para fechada
      }
    },

    async fetchRules() {
      const projectId = parseInt(this.$route.params.id, 10)
      if (isNaN(projectId)) {
        this.error = 'ID de projeto inválido.'
        return
      }
      this.loading = true
      this.error = ''
      const { fetchRules, fetchClosedRules } = useRuleVoting()
      try {
        let openRules: RuleDTO[] = []
        let closedRules: RuleDTO[] = []

        // Sempre busca ambas as listas para permitir filtragem local completa
        openRules = await fetchRules(projectId)
        closedRules = await fetchClosedRules(projectId)
        
        // Combina as regras e garante que cada regra tem user_has_voted e vote
        const allRules = [...openRules, ...closedRules]
        this.rules = allRules.map(rule => {
          // fetchRules e fetchClosedRules já deveriam trazer user_has_voted e vote
          // mas garantimos que as propriedades existem para o template
          return {
            ...rule,
            user_has_voted: rule.user_has_voted !== undefined ? rule.user_has_voted : false,
            vote: rule.vote !== undefined ? rule.vote : null
          }
        });

      } catch (err: any) {
        this.error = err.response?.data?.error || 'Falha ao carregar regras. Por favor, tente mais tarde.'
        this.snackbarMessage = this.error
        this.snackbarColor = 'error'
        this.snackbar = true
      } finally {
        this.loading = false
      }
    },

    async voteRule(ruleId: number, vote: boolean) {
      const projectId = parseInt(this.$route.params.id, 10)
      if (isNaN(projectId)) return

      const { voteRule: serviceVoteRule } = useRuleVoting()
      try {
        await serviceVoteRule(projectId, [{ rule_id: ruleId, vote }])
        this.snackbarMessage = 'Voto registado com sucesso!'
        this.snackbarColor = 'success'
        this.snackbar = true
        await this.fetchRules() // Recarrega as regras para atualizar o estado
      } catch (err: any) {
        this.snackbarMessage = err.response?.data?.message || 'Falha ao registar voto. Tente novamente.'
        this.snackbarColor = 'error'
        this.snackbar = true
      }
    },

    async closeVoting(ruleId: number) {
      const projectId = parseInt(this.$route.params.id, 10)
      if (isNaN(projectId)) return

      const { closeVoting: serviceCloseVoting } = useRuleVoting()
      try {
        await serviceCloseVoting(projectId, ruleId)
        this.snackbarMessage = 'Votação encerrada com sucesso!'
        this.snackbarColor = 'success'
        this.snackbar = true
        await this.fetchRules() // Recarrega as regras para atualizar o estado
      } catch (err: any) {
        this.snackbarMessage = err.response?.data?.message || 'Falha ao encerrar votação. Tente novamente.'
        this.snackbarColor = 'error'
        this.snackbar = true
      }
    }
  }
})
</script>

<style scoped>
/* Adicione estilos específicos para esta página aqui, se necessário */
</style> 