<template>
  <v-container class="pa-5 mt-16">
    <v-card>
      <v-card-title>
        Votação de Regras de Anotação
        <v-spacer />
        <v-btn text aria-label="Voltar" @click="$router.back()">
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </v-card-title>

      <v-btn color="success" class="ma-4" @click="confirmCloseAllRules">
        <v-icon left>{{ mdiStopCircleOutline }}</v-icon>
        Close All Open Rules
      </v-btn>

      <v-dialog v-model="confirmDialog" max-width="400">
        <v-card>
          <v-card-title>Confirmar Encerramento</v-card-title>
          <v-card-text>
            Tem certeza que deseja encerrar todas as regras abertas?
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="confirmDialog = false">Cancelar</v-btn>
            <v-btn color="success" @click="closeAllOpenRules">Confirmar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-alert v-if="error" type="error" dense class="mb-4">{{ error }}</v-alert>
      <v-progress-circular v-if="loading" indeterminate class="ma-4" />

      <v-data-table
        v-if="rules.length"
        :headers="headers"
        :items="rules"
        item-key="id"
        class="elevation-1 mt-4"
      >
        <template #[`item.votes_yes`]="{ item }">{{ item.votes_yes }}</template>
        <template #[`item.votes_no`]="{ item }">{{ item.votes_no }}</template>

        <template #[`item.action`]="{ item }">
          <v-btn
            icon
            :color="votes[item.rule.id] === true ? 'success' : 'grey lighten-1'"
            :disabled="!item.is_open"
            @click="setVote(item.rule.id, true)"
          >👍</v-btn>
          <v-btn
            icon
            :color="votes[item.rule.id] === false ? 'error' : 'grey lighten-1'"
            :disabled="!item.is_open"
            @click="setVote(item.rule.id, false)"
          >👎</v-btn>
        </template>
      </v-data-table>

      <div v-if="!loading && !rules.length" class="text-gray-600 mt-4">
        Nenhuma regra encontrada para este projeto.
      </div>

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
          :disabled="loading || !Object.keys(votes).length"
          @click="clearVotes"
        >Cancelar</v-btn>
      </div>

      <v-snackbar v-model="snackbar" top :color="snackbarColor" :timeout="3000">
        {{ snackbarMessage }}
      </v-snackbar>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiArrowLeft, mdiStopCircleOutline } from '@mdi/js'
import { useRuleVoting } from '~/composables/useRuleVoting'
import type { RuleDTO } from '@/repositories/rule/apiRuleRepository'

export default Vue.extend({
  data() {
    return {
      rules: [] as RuleDTO[],
      loading: false,
      error: '',
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success' as 'success' | 'error' | 'info',
      votes: {} as Record<number, boolean>,
      confirmDialog: false,

      headers: [
        { text: 'Regra', value: 'rule.text' },
        { text: 'Sim', value: 'votes_yes' },
        { text: 'Não', value: 'votes_no' },
        { text: 'Ação', value: 'action', sortable: false }
      ],

      mdiArrowLeft,
      mdiStopCircleOutline
    }
  },

  computed: {
    openRulesCount(): number {
      return this.rules.filter(r => r.is_open).length
    },
    canSubmitVotes(): boolean {
      const openIds = this.rules.filter(r => r.is_open).map(r => r.rule.id)
      return openIds.every(id => this.votes[id] !== undefined)
    }
  },

  created() {
    this.fetchRules()
  },

  methods: {
    /* ---------- carregar ---------- */
    async fetchRules() {
      const projectId = Number(this.$route.params.id)
      if (!projectId) {
        this.error = 'ID de projeto inválido.'; return
      }
      this.loading = true; this.error = ''
      const { fetchRules } = useRuleVoting()
      try {
        this.rules = await fetchRules(projectId)
      } catch (e: any) {
        this.error = e.response?.data?.error || 'Falha ao carregar regras.'
      } finally {
        this.loading = false
      }
    },

    /* ---------- votar ---------- */
    setVote(ruleId: number, vote: boolean) {
      if (this.votes[ruleId] === vote) this.$delete(this.votes, ruleId)
      else this.$set(this.votes, ruleId, vote)
    },

    async submitVotes() {
      if (!this.canSubmitVotes) {
        this.showSnack('Vote em todas as regras abertas.', 'error'); return
      }
      const projectId = Number(this.$route.params.id)
      const { voteRule } = useRuleVoting()
      this.loading = true
      try {
        const payload = Object.entries(this.votes).map(([id, v]) => ({
          rule_id: Number(id), vote: v
        }))
        await voteRule(projectId, payload)
        this.showSnack('Votos enviados!', 'success')
        this.votes = {}
        await this.fetchRules()
      } catch (e: any) {
        this.showSnack(e.response?.data?.error || 'Erro ao enviar votos.', 'error')
      } finally {
        this.loading = false
      }
    },

    clearVotes() { this.votes = {} },

    /* ---------- encerrar ---------- */
    confirmCloseAllRules() {
      this.confirmDialog = true
    },

    async closeAllOpenRules() {
      this.confirmDialog = false
      const projectId = Number(this.$route.params.id)
      if (!projectId) return
      const { closeVoting } = useRuleVoting()
      this.loading = true

      let successCount = 0
      let failCount = 0

      for (const r of this.rules.filter(r => r.is_open)) {
        try {
          await closeVoting(projectId, r.rule.id)
          successCount++
        } catch {
          failCount++
        }
      }

      if (successCount)
        this.showSnack(`${successCount} votação(ões) encerrada(s).`, 'success')
      if (failCount)
        this.showSnack(`${failCount} falha(s) ao encerrar.`, 'error')

      this.loading = false
      this.$router.push(this.localePath(`/projects/${projectId}/rules/closed`))
    },

    /* ---------- util ---------- */
    showSnack(msg: string, color: 'success'|'error'|'info') {
      this.snackbarMessage = msg; this.snackbarColor = color; this.snackbar = true
    }
  }
})
</script>

<style scoped>
.vote-actions { display: flex; align-items: center; }
.v-btn { margin: 0 2px; }
</style>
