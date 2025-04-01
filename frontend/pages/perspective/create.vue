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
          <v-card-text>
            Quer mesmo criar uma perspetiva nova?
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="dialogConfirm = false">Cancelar</v-btn>
            <v-btn color="green darken-1" text @click="confirmarEnvio">Confirmar</v-btn>
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
        dialogConfirm: false
      }
    },
    async mounted() {
      try {
        const res = await this.$axios.get('/v1/projects/without-perspectives')
        this.projectOptions = res.data
      } catch (err) {
        console.error('Erro ao carregar projetos:', err)
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
          alert("Preenche todos os campos obrigatórios.")
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
  
          await this.$axios.post(`/api/projects/${payload.project}/perspectives`, payload)
          alert('Perspetiva criada com sucesso!')
          this.$router.push('/projects')
        } catch (err) {
          console.error('Erro ao criar perspetiva:', err)
          alert('Erro ao criar perspetiva.')
        }
      }
    }
  }
  </script>
  