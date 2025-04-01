<template>
    <v-container>
      <v-card>
        <v-card-title>Criar Perspetiva</v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-text-field v-model="name" label="Nome da Perspetiva" required />
            <v-select
              v-model="projectId"
              :items="projectOptions"
              label="Selecionar Projeto"
              item-text="name"
              item-value="id"
              required
            />
  
            <v-divider class="my-4" />
            <h3>Campos</h3>
  
            <div v-for="(field, index) in fields" :key="index" class="mb-4">
              <v-text-field v-model="field.name" label="Nome do campo" required />
              <v-select
                v-model="field.type"
                :items="fieldTypes"
                label="Tipo"
                required
              />
              <v-text-field
                v-if="field.type === 'choice'"
                v-model="field.optionsString"
                label="Opções (separadas por vírgula)"
                @change="updateOptions(field)"
              />
              <v-btn icon @click="removeField(index)">
                <v-icon color="red">mdi-delete</v-icon>
              </v-btn>
            </div>
  
            <v-btn color="primary" @click.prevent="addField">Adicionar Campo</v-btn>
          </v-form>
        </v-card-text>
  
        <v-card-actions>
          <v-btn color="success" type="button" @click.prevent="confirmarCriacao">Criar</v-btn>
        </v-card-actions>
      </v-card>
  
      <!-- Diálogo de Confirmação -->
      <v-dialog v-model="dialogConfirm" max-width="500">
        <v-card>
          <v-card-title class="headline">Confirmação</v-card-title>
          <v-card-text> Criar uma perspetiva nova? </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="dialogConfirm = false">Cancelar</v-btn>
            <v-btn color="green darken-1" text @click="confirmarEnvio">Confirmar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
      <!-- Diálogo de Resultado -->
      <v-dialog v-model="dialogResultado.show" max-width="400">
        <v-card>
          <v-card-title class="headline">{{ dialogResultado.titulo }}</v-card-title>
          <v-card-text>{{ dialogResultado.mensagem }}</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" text @click="fecharResultado">Fechar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script>
  export default {
    data() {
      return {
        name: '',
        projectId: null,
        fields: [],
        projectOptions: [],
        fieldTypes: ['string', 'integer', 'boolean', 'choice'],
        dialogConfirm: false,
        dialogResultado: {
          show: false,
          titulo: '',
          mensagem: ''
        }
      }
    },
    async mounted() {
      try {
        const res = await this.$axios.get('/v1/projects/without-perspectives')
        this.projectOptions = res.data
      } catch (err) {
        this.mostrarResultado('Erro', 'Erro ao carregar projetos.')
        console.error(err)
      }
    },
    methods: {
      addField() {
        this.fields.push({ name: '', type: 'string', options: [], optionsString: '' })
      },
      removeField(index) {
        this.fields.splice(index, 1)
      },
      updateOptions(field) {
        field.options = field.optionsString.split(',').map(opt => opt.trim())
      },
      confirmarCriacao() {
        if (!this.name || !this.projectId) {
          this.mostrarResultado('Erro', 'Preenche todos os campos obrigatórios.')
          return
        }
        this.dialogConfirm = true
      },
      async confirmarEnvio() {
        this.dialogConfirm = false
        try {
          const payload = {
            name: this.name,
            project: parseInt(this.projectId),
            type: 'string',
            fields: this.fields.map(field => ({
              name: field.name,
              type: field.type,
              options: field.type === 'choice' ? field.options : null
            }))
          }
  
          await this.$axios.post(`/v1/projects/${payload.project}/perspectives`, payload)
          this.mostrarResultado('Sucesso', 'Perspetiva criada com sucesso!')
        } catch (err) {
          this.mostrarResultado('Erro', 'Erro ao criar perspetiva.')
          console.error(err)
        }
      },
      mostrarResultado(titulo, mensagem) {
        this.dialogResultado.titulo = titulo
        this.dialogResultado.mensagem = mensagem
        this.dialogResultado.show = true
      },
      fecharResultado() {
        this.dialogResultado.show = false
        if (this.dialogResultado.titulo === 'Sucesso') {
          this.$router.push('/projects')
        }
      }
    }
  }
  </script>
  