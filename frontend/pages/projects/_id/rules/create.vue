<template>
    <v-container class="pa-5 mt-16">
      <v-card>
        <v-card-title>Criar Nova Regra de Anotação</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-text-field
              v-model="ruleText"
              label="Texto da Regra"
              :rules="[rules.required]"
              required
            ></v-text-field>
  
            <v-btn :disabled="!valid" color="primary" @click="createRule">
              Criar Regra
            </v-btn>
          </v-form>
  
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
  
  export default Vue.extend({
    data() {
      return {
        ruleText: '',
        valid: false,
        snackbar: false,
        snackbarMessage: '',
        snackbarColor: 'success' as 'success' | 'error',
        rules: {
          required: (v: string) => !!v || 'Este campo é obrigatório.'
        }
      }
    },
    methods: {
      async createRule() {
        const projectId = parseInt(this.$route.params.id, 10)
        const { createRule } = useRuleVoting()
  
        try {
          await createRule(projectId, { text: this.ruleText })
          this.snackbarMessage = 'Regra criada com sucesso!'
          this.snackbarColor = 'success'
          this.$router.push(this.localePath(`/projects/${projectId}/rules`))
        } catch (err: any) {
          this.snackbarMessage =
            err.response?.data?.error || 'Erro ao criar regra.'
          this.snackbarColor = 'error'
        } finally {
          this.snackbar = true
        }
      }
    }
  })
  </script>
  
  <style scoped>
  /* Estilos personalizados */
  </style>
  