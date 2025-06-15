<template>
  <v-container class="pa-5 mt-16">
    <v-card>
      <v-card-title>Votação de Regras de Anotação</v-card-title>

      <v-card-text>
        <!-- Erro ao carregar -->
        <v-alert v-if="error" type="error" dense class="mb-4">
          {{ error }}
        </v-alert>

        <!-- Loading spinner -->
        <v-progress-circular v-if="loading" indeterminate class="ma-4" />

        <!-- Tabela de regras -->
        <v-data-table
          v-if="rules.length"
          :headers="headers"
          :items="rules"
          item-key="id"
          class="elevation-1 mt-4"
        >
          <!-- Coluna "Sim" -->
          <template #[`item.votes_yes`]="{ item }">
            {{ item.votes_yes }}
          </template>

          <!-- Coluna "Não" -->
          <template #[`item.votes_no`]="{ item }">
            {{ item.votes_no }}
          </template>

          <!-- Coluna de Ações -->
          <template #[`item.action`]="{ item }">
            <v-btn
              icon
              :color="votes[item.rule.id] === true ? 'success' : 'grey lighten-1'"
              :disabled="!item.is_open"
              @click="setVote(item.rule.id, true)"
            >
              👍
            </v-btn>
            <v-btn
              icon
              :color="votes[item.rule.id] === false ? 'error' : 'grey lighten-1'"
              :disabled="!item.is_open"
              @click="setVote(item.rule.id, false)"
            >
              👎
            </v-btn>
          </template>
        </v-data-table>

        <!-- Nenhuma regra -->
        <div v-if="!loading && !rules.length" class="text-gray-600 mt-4">
          Nenhuma regra encontrada para este projeto.
        </div>

        <!-- Snackbar de feedback -->
        <v-snackbar v-model="snackbar" top :color="snackbarColor" :timeout="3000">
          {{ snackbarMessage }}
        </v-snackbar>

        <div class="vote-actions">
          <v-btn
            color="primary"
            class="mt-4 mr-2"
            :loading="loading"
            :disabled="!canSubmitVotes"
            @click="submitVotes"
          >
            Submeter Votos ({{ Object.keys(votes).length }}/{{ openRulesCount }})
          </v-btn>
          <v-btn
            color="secondary"
            class="mt-4"
            :disabled="loading || Object.keys(votes).length === 0"
            @click="clearVotes"
          >
            Cancelar
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { useRuleVoting } from '~/composables/useRuleVoting'
import type { RuleDTO } from '@/repositories/rule/apiRuleRepository'

export default Vue.extend({
  data() {
    return {
      rules: [] as RuleDTO[],
      loading: false,
      error: '' as string,
      snackbar: false as boolean,
      snackbarMessage: '' as string,
      snackbarColor: 'success' as 'success' | 'error',
      votes: {} as Record<number, boolean>,
      headers: [
        { text: 'Regra', value: 'rule.text' },
        { text: 'Sim', value: 'votes_yes' },
        { text: 'Não', value: 'votes_no' },
        { text: 'Ação', value: 'action', sortable: false }
      ]
    }
  },
  computed: {
    openRulesCount(): number {
      return this.rules.filter(rule => rule.is_open).length
    },
    canSubmitVotes(): boolean {
      const openRuleIds = this.rules
        .filter(rule => rule.is_open)
        .map(rule => rule.rule.id)
      return openRuleIds.every(id => this.votes[id] !== undefined)
    }
  },
  created() {
    this.fetchRules()
  },
  methods: {
    async fetchRules() {
      const projectId = parseInt(this.$route.params.id, 10)
      if (isNaN(projectId)) {
        this.error = 'ID de projeto inválido.'
        return
      }
      this.loading = true
      this.error = ''
      const { fetchRules } = useRuleVoting()
      try {
        this.rules = await fetchRules(projectId)
      } catch (err: any) {
        this.error = err.response?.data?.error || 'Falha ao carregar regras. Por favor, tente mais tarde.'
        this.snackbarMessage = this.error
        this.snackbarColor = 'error'
        this.snackbar = true
      } finally {
        this.loading = false
      }
    },
    setVote(ruleId: number, vote: boolean) {
      console.log('Setting vote:', { ruleId, vote, currentVotes: this.votes })
      if (this.votes[ruleId] === vote) {
        this.$delete(this.votes, ruleId)
      } else {
        this.$set(this.votes, ruleId, vote)
      }
      console.log('Votes after update:', this.votes)
    },
    async submitVotes() {
      if (!this.canSubmitVotes) {
        this.snackbarMessage = 'Por favor, vote em todas as regras abertas antes de submeter.'
        this.snackbarColor = 'error'
        this.snackbar = true
        return
      }

      const projectId = parseInt(this.$route.params.id, 10)
      if (isNaN(projectId)) {
        this.error = 'ID de projeto inválido.'
        return
      }
      this.loading = true
      this.error = ''
      const { voteRule } = useRuleVoting()
      try {
        const voteData = Object.entries(this.votes).map(([ruleId, vote]) => ({
          rule_id: parseInt(ruleId),
          vote
        }))
        await voteRule(projectId, voteData)
        this.snackbarMessage = 'Votos enviados com sucesso!'
        this.snackbarColor = 'success'
        this.snackbar = true
        this.votes = {}
        await this.fetchRules()
      } catch (err: any) {
        this.error = err.response?.data?.error || 'Falha ao enviar votos. Por favor, tente mais tarde.'
        this.snackbarMessage = this.error
        this.snackbarColor = 'error'
        this.snackbar = true
      } finally {
        this.loading = false
      }
    },
    clearVotes() {
      this.votes = {}
    }
  }
})
</script>

<style scoped>
.vote-actions {
  display: flex;
  align-items: center;
}
.v-btn {
  margin: 0 2px;
}
</style>