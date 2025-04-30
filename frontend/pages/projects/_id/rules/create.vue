<!-- frontend/pages/projects/_id/rules/create.vue -->
<template>
  <v-container class="pa-5 mt-16">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Criar Regra de Anotação</span>
        <v-btn text @click="$router.back()">← Voltar</v-btn>
      </v-card-title>

      <v-card-text>
        <v-form ref="form" v-model="valid" @submit.prevent="createRule">
          <v-textarea
            v-model="ruleText"
            label="Texto da Regra"
            :rules="[rules.required, rules.minLength]"
            outlined
            rows="3"
            auto-grow
            placeholder="Exemplo: 'Marcar todas as datas no formato DD/MM/AAAA como ENTITY_DATE'"
          ></v-textarea>

          <v-checkbox
            v-model="startOpen"
            label="Abrir votação imediatamente"
            :value="true"
          ></v-checkbox>

          <div class="d-flex justify-end mt-4">
            <v-btn
              color="primary"
              type="submit"
              :disabled="!valid"
              :loading="loading"
              large
            >
              Criar Regra
            </v-btn>
          </div>
        </v-form>

        <v-snackbar v-model="snackbar" top :color="snackbarColor">
          {{ snackbarMessage }}
          <v-btn text @click="snackbar = false">Fechar</v-btn>
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
      startOpen: true,
      valid: false,
      loading: false,
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success',
      rules: {
        required: (v: string) => !!v || 'Texto da regra é obrigatório',
        minLength: (v: string) => 
          (v && v.length >= 15) || 'A regra deve ter pelo menos 15 caracteres'
      }
    }
  },
  methods: {
    async createRule() {
      if (!this.valid) return
      
      this.loading = true
      const projectId = parseInt(this.$route.params.id, 10)
      const { createRule } = useRuleVoting()

      try {
        await createRule(projectId, {
          text: this.ruleText,
          is_open: this.startOpen
        })
        
        this.snackbarMessage = 'Regra criada com sucesso!'
        this.snackbarColor = 'success'
        this.$router.push(`/projects/${projectId}/rules`)
      } catch (error) {
        this.snackbarMessage = error.response?.data?.error || 'Erro ao criar regra'
        this.snackbarColor = 'error'
      } finally {
        this.loading = false
        this.snackbar = true
      }
    }
  }
})
</script>