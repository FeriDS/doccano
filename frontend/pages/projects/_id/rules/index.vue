<template>
  <v-container class="pa-5 mt-16">
    <div class="d-flex justify-space-between mb-4">
      <v-btn color="primary" @click="goToCreate">
        Criar nova regra
      </v-btn>

      <v-btn color="primary" @click="goToClosed">
        Ver votações terminadas
      </v-btn>
    </div>

    <v-card>
      <v-card-title>Votação de Regras de Anotação</v-card-title>

      <v-card-text>
        <v-alert v-if="error" type="error" dense class="mb-4">
          {{ error }}
        </v-alert>

        <v-progress-circular v-if="loading" indeterminate class="ma-4" />

        <v-data-table
          v-if="openRules.length"
          :headers="headers"
          :items="openRules"
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
            <div class="d-flex">
              <v-avatar
                size="40"
                v-if="item.vote === true"
                color="green lighten-4"
                class="mr-2"
              >
                <v-btn
                  icon
                  depressed
                  :disabled="!item.is_open"
                  color="green darken-2"
                  class="text-white"
                  @click="onVote(item.id, true)"
                >
                  👍
                </v-btn>
              </v-avatar>

              <v-btn
                v-else
                icon
                depressed
                :disabled="!item.is_open"
                :color="item.vote === false ? 'grey lighten-1' : 'green lighten-4'"
                :class="item.vote === false ? 'text--secondary' : 'text--secondary'"
                @click="onVote(item.id, true)"
              >
                👍
              </v-btn>

              <v-avatar
                size="40"
                v-if="item.vote === false"
                color="red lighten-4"
                class="ml-2"
              >
                <v-btn
                  icon
                  depressed
                  :disabled="!item.is_open"
                  color="red darken-2"
                  class="text-white"
                  @click="onVote(item.id, false)"
                >
                  👎
                </v-btn>
              </v-avatar>

              <v-btn
                v-else
                icon
                depressed
                :disabled="!item.is_open"
                :color="item.vote === true ? 'grey lighten-1' : 'red lighten-4'"
                :class="item.vote === true ? 'text--secondary' : 'text--secondary'"
                class="ml-2"
                @click="onVote(item.id, false)"
              >
                👎
              </v-btn>
            </div>
          </template>

          <template #[`item.close`]="{ item }">
            <v-btn
              small
              color="warning"
              @click="closeVoting(item.id)"
            >
              Encerrar
            </v-btn>
          </template>
        </v-data-table>

        <div v-if="!loading && !openRules.length" class="text-gray-600 mt-4">
          Nenhuma regra disponível para votação neste momento.
        </div>

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
      error: '',
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success' as 'success' | 'error',
      headers: [
        { text: 'Regra', value: 'rule.text' },
        { text: 'Sim', value: 'votes_yes' },
        { text: 'Não', value: 'votes_no' },
        { text: 'Ação', value: 'action', sortable: false },
        { text: 'Encerrar Votação', value: 'close', sortable: false }
      ]
    }
  },

  computed: {
    openRules(): RuleDTO[] {
      return this.rules.filter(rule => rule.is_open === true)
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
      const { fetchRules } = useRuleVoting()

      try {
        this.rules = await fetchRules(projectId)
      } catch (err: any) {
        this.error =
          err.response?.data?.error || 'Falha ao carregar regras. Por favor, tente mais tarde.'
      } finally {
        this.loading = false
      }
    },

    async onVote(ruleId: number, choice: boolean) {
      const projectId = parseInt(this.$route.params.id, 10)
      const { voteRule } = useRuleVoting()

      try {
        const result: VoteResultDTO = await voteRule(projectId, ruleId, choice)
        const idx = this.rules.findIndex(r => r.id === ruleId)
        if (idx !== -1) {
          this.rules.splice(idx, 1, {
            ...this.rules[idx],
            ...result,
            user_has_voted: true,
            vote: choice
          })
        }

        this.snackbarMessage = 'Voto registado.'
        this.snackbarColor = 'success'
      } catch (err: any) {
        this.snackbarMessage =
          err.response?.data?.error || 'Erro ao votar. Tente novamente.'
        this.snackbarColor = 'error'
      } finally {
        this.snackbar = true
      }
    },

    async closeVoting(ruleId: number) {
      const projectId = parseInt(this.$route.params.id, 10)
      const { closeVoting } = useRuleVoting()

      try {
        await closeVoting(projectId, ruleId)

        const idx = this.rules.findIndex(r => r.id === ruleId)
        if (idx !== -1) {
          this.rules[idx].is_open = false
        }

        this.snackbarMessage = 'Votação encerrada com sucesso.'
        this.snackbarColor = 'success'
      } catch (err: any) {
        this.snackbarMessage =
          err.response?.data?.error || 'Erro ao encerrar votação.'
        this.snackbarColor = 'error'
      } finally {
        this.snackbar = true
      }
    },

    goToClosed() {
      const projectId = this.$route.params.id
      this.$router.push(this.localePath(`/projects/${projectId}/rules/closed`))
    },

    goToCreate() {
      const projectId = this.$route.params.id
      this.$router.push(this.localePath(`/projects/${projectId}/rules/create`))
    }
  }
})
</script>

<style scoped>
/* Estilos personalizados */
</style>
