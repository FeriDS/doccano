<template>
    <v-container class="pa-5 mt-16">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Votações Terminadas</span>
          <v-btn text @click="goBack">← Voltar</v-btn>
        </v-card-title>
  
        <v-card-text>
          <v-progress-circular v-if="loading" indeterminate class="ma-4" />
          <v-list v-if="rules.length">
            <v-list-item v-for="rule in rules" :key="rule.id">
              <v-list-item-content>
                <v-list-item-title>{{ rule.rule.text }}</v-list-item-title>
                <v-list-item-subtitle>
                  Sim: {{ rule.votes_yes }} | Não: {{ rule.votes_no }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
  
          <div v-if="!loading && !rules.length" class="text-gray-600 mt-4">
            Nenhuma votação encerrada encontrada.
          </div>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import { useRuleVoting } from '@/composables/useRuleVoting'
  import type { RuleDTO } from '@/repositories/rule/apiRuleRepository'
  
  export default Vue.extend({
    data() {
      return {
        rules: [] as RuleDTO[],
        loading: false
      }
    },
  
    created() {
      this.fetchClosedRules()
    },
  
    methods: {
      async fetchClosedRules() {
        this.loading = true
        const projectId = parseInt(this.$route.params.id, 10)
        const { fetchClosedRules } = useRuleVoting()
        try {
          this.rules = await fetchClosedRules(projectId)
        } catch (err) {
          console.error('Erro ao carregar votações encerradas', err)
        } finally {
          this.loading = false
        }
      },
  
      goBack() {
        this.$router.back()
      }
    }
  })
  </script>
  