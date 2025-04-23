<template>
    <v-container class="pa-5 mt-16">
        <v-card elevation="2">
            <v-card-title>Preencher Perspetiva</v-card-title>
            <v-card-text>
                <v-form ref="form" @submit.prevent="submit">
                    <div v-for="field in fields" :key="field.id" class="my-3">
                    <v-text-field
                        v-if="field.field_type === 'string'"
                        v-model="answers[field.id]"
                        :label="field.name"
                        :hint="field.description"
                        :rules="[v => !!v || 'Este campo é obrigatório']"
                        persistent-hint
                        outlined
                    />
                    <v-text-field
                        v-else-if="field.field_type === 'int'"
                        v-model.number="answers[field.id]"
                        type="number"
                        :label="field.name"
                        :hint="field.description"
                        :rules="[v => v !== null && v !== '' || 'Este campo é obrigatório']"
                        persistent-hint
                        outlined
                    />
                    <v-checkbox
                        v-else-if="field.field_type === 'bool'"
                        v-model="answers[field.id]"
                        :label="field.name"
                        :hint="field.description"
                    />
                    </div>

                    <!-- Botões -->
                    <v-row justify="end" class="mt-4">
                        <v-btn
                            text
                            color="grey"
                            class="mr-2"
                            @click="cancel"
                            
                            >
                            Cancelar
                        </v-btn>

                        <v-btn
                            color="primary"
                            type="submit"
                            :disabled="isSubmitting"
                            >
                            {{ isSubmitting ? 'A guardar...' : 'Guardar' }}
                        </v-btn>
                        <!-- Snackbar para mensagens -->
                    
                    </v-row>
                </v-form>
            </v-card-text>
        </v-card>

        <v-snackbar
            v-model="snackbar"
            :color="snackbarColor"
            :timeout="3000"
            top
            >
            {{ snackbarMessage }}
        </v-snackbar>
    </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { getLinkToAnnotationPage } from '@/presenter/linkToAnnotationPage'

export default Vue.extend({
  data() {
    return {
      fields: [] as any[],
      answers: {} as Record<number, string | number | boolean>,
      isSubmitting: false,
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success', // ou 'error' dinamicamente
      project: null as any
    }
  },
  async created() {
    const projectId = this.$route.params.id
    this.project = await this.$repositories.project.findById(projectId)
    try {
      this.fields = await this.$services.perspective.fetchPerspectiveFields(parseInt(projectId))
      
      if (!this.fields.length) {
        this.snackbarMessage = 'Não há perspetiva associada a este projeto.'
        this.snackbarColor = 'error'
        this.snackbar = true
        return
      }

      this.fields.forEach(field => {
        this.answers[field.id] = field.field_type === 'bool' ? false : ''
      })
    } catch (error) {
      this.snackbarMessage =
      error.response?.data?.error || 'Erro ao carregar campos da perspetiva.'
      this.snackbarColor = 'error'
      this.snackbar = true
    }
  },

  methods: {
    async submit() {
      const form = this.$refs.form as any
      if (!form?.validate?.() ) {
        this.snackbarMessage = 'Por favor, preencha todos os campos obrigatórios.'
        this.snackbarColor = 'error'
        this.snackbar = true
        return
      }
      const projectId = parseInt(this.$route.params.id)
      this.isSubmitting = true
      try {
        await this.$services.perspective.submitAnswers(projectId, this.answers)
        this.snackbarMessage = 'Perspetiva preenchida com sucesso.'
        this.snackbarColor = 'success'
        this.snackbar = true
        // Aguarda e redireciona para página de anotação
        setTimeout(() => {
          const link = getLinkToAnnotationPage(projectId, this.project.projectType)
          this.$router.push(this.localePath({ path: link, query: { page: '1' } }))
        }, 1500)
      } catch (error) {
        if (!error.response) {
          // Erro de rede, ex: base de dados desligada, backend caiu, etc.
          this.snackbarMessage = 'Erro de rede: não foi possível ligar ao servidor.'
        } else if (error.response.status >= 500) {
          this.snackbarMessage = 'Erro do servidor: verifique a ligação com a base de dados.'
        } else {
          this.snackbarMessage = error.response.data?.error || 'Erro ao guardar respostas da perspetiva.'
        }
        this.snackbarColor = 'error'
        this.snackbar = true
      } finally {
        this.isSubmitting = false
      }
    },
    cancel() {
        const projectId = parseInt(this.$route.params.id)
        this.$router.push(`/projects/${projectId}`)
    }
  }
})
</script>
