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
              <v-text-field
                v-model="field.name"
                label="Nome do campo"
                required
              />
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
  
            <v-btn color="primary" @click="addField">Adicionar Campo</v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn color="success" @click="submit">Criar</v-btn>
        </v-card-actions>
      </v-card>
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
      fieldTypes: ['string', 'integer', 'boolean', 'choice']
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
    async submit() {
      try {
        const payload = {
          name: this.name,
          type: 'string',
          project: parseInt(this.projectId),
          fields: this.fields.map(f => {
            const base = { name: f.name, type: f.type }
            if (f.type === 'choice') base.options = f.options
            return base
          })
        }

        await this.$axios.post(`/api/projects/${payload.project}/perspectives`, payload)
        this.$router.push('/projects')
      } catch (err) {
        console.error('Erro ao criar perspetiva:', err)
      }
    }
  }
}

</script>
