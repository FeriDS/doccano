<template>
  <v-container class="pa-5 mt-16">
    <!-- BOTÃO NO TOPO -->
    <div class="d-flex justify-end mb-4">
      <v-btn color="primary" @click="goToClosed">
        Ver votações terminadas
      </v-btn>
    </div>
    <!-- CARTÃO COM LISTAGEM DE VOTAÇÕES ABERTAS -->
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
          <template #[`item.votes_yes`]="{ item }">
            {{ item.votes_yes }}
          </template>

          <template #[`item.votes_no`]="{ item }">
            {{ item.votes_no }}
          </template>

          <template #[`item.action`]="{ item }">
            <v-btn
              icon
              color="green"
              :disabled="item.user_has_voted || !item.is_open"
              @click="onVote(item.id, true)"
            >
              👍
            </v-btn>
            <v-btn
              icon
              color="red"
              :disabled="item.user_has_voted || !item.is_open"
              @click="onVote(item.id, false)"
            >
              👎
            </v-btn>
          </template>
        </v-data-table>

        <!-- Nenhuma regra com votação aberta -->
        <div v-if="!loading && !rules.length" class="text-gray-600 mt-4">
          Nenhuma regra disponível para votação neste momento.
        </div>

        <!-- Snackbar de feedback -->
        <v-snackbar v-model="snackbar" top :color="snackbarColor" :timeout="3000">
          {{ snackbarMessage }}
        </v-snackbar>
      </v-card-text>
    </v-card>

   
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { useRuleVoting } from '@/composables/useRuleVoting'
import type { RuleDTO, VoteResultDTO } from '@/repositories/rule/apiRuleRepository'

export default Vue.extend({
  data() {
    return {
      rules: [] as RuleDTO[],
      loading: false,
      error: '' as string,
      snackbar: false as boolean,
      snackbarMessage: '' as string,
      snackbarColor: 'success' as 'success' | 'error',
      headers: [
        { text: 'Regra', value: 'rule.text' },
        { text: 'Sim', value: 'votes_yes' },
        { text: 'Não', value: 'votes_no' },
        { text: 'Ação', value: 'action', sortable: false }
      ]
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
        this.error =
          err.response?.data?.error ||
          'Falha ao carregar regras. Por favor, tente mais tarde.'
      } finally {
        this.loading = false
      }
    },

    async onVote(ruleId: number, choice: boolean) {
      const projectId = parseInt(this.$route.params.id, 10)
      if (isNaN(projectId)) {
        this.error = 'ID de projeto inválido.'
        return
      }

      const { voteRule } = useRuleVoting()

      try {
        const result: VoteResultDTO = await voteRule(
          projectId,
          ruleId,
          choice
        )
        const idx = this.rules.findIndex(r => r.id === ruleId)
        if (idx !== -1) {
          this.rules.splice(idx, 1, { ...this.rules[idx], ...result })
        }

        this.snackbarMessage = 'Voto registado com sucesso.'
        this.snackbarColor = 'success'
      } catch (err: any) {
        this.snackbarMessage =
          err.response?.data?.error || 'Erro ao votar. Tente novamente.'
        this.snackbarColor = 'error'
      } finally {
        this.snackbar = true
      }
    },

    goToClosed() {
      const projectId = this.$route.params.id
      this.$router.push(this.localePath(`/projects/${projectId}/rules/closed`))
    }
  }
})
</script>

<style scoped>
/* Estilos personalizados (opcional) */
</style>
