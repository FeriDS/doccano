<template>
  <v-card>
    <v-card-title>
      {{ isAdmin ? 'Configurar Perspetiva' : 'Preencher Perspetiva Pessoal' }}
    </v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <template v-if="isAdmin">
          <v-switch
            v-model="perspective.is_required"
            label="Exigir preenchimento antes da anotação"
            class="mb-4"
          />
        </template>

        <div v-if="isAdmin" class="mb-4">
          <v-btn
            color="primary"
            @click="addField"
          >
            <v-icon left>mdi-plus</v-icon>
            Adicionar Campo
          </v-btn>
        </div>

        <v-row>
          <v-col
            v-for="(field, index) in fields"
            :key="field.id || index"
            cols="12"
          >
            <v-card outlined>
              <v-card-text>
                <template v-if="isAdmin">
                  <!-- Field Configuration -->
                  <v-row>
                    <v-col cols="6">
                      <v-text-field
                        v-model="field.name"
                        label="Nome do Campo"
                        :rules="[v => !!v || 'Nome é obrigatório']"
                        required
                      />
                    </v-col>
                    <v-col cols="6">
                      <v-select
                        v-model="field.field_type"
                        :items="fieldTypes"
                        label="Tipo de Campo"
                        required
                      />
                    </v-col>
                  </v-row>
                  <v-textarea
                    v-model="field.description"
                    label="Descrição"
                    rows="2"
                  />
                  <v-switch
                    v-model="field.required"
                    label="Campo Obrigatório"
                  />
                  
                  <!-- Options for choice fields -->
                  <template v-if="['Choice', 'MultipleChoice'].includes(field.field_type)">
                    <v-text-field
                      v-model="newOption[field.id || index]"
                      label="Nova Opção"
                      append-outer-icon="mdi-plus"
                      @click:append-outer="addOption(field)"
                      @keyup.enter="addOption(field)"
                    />
                    <v-chip-group column>
                      <v-chip
                        v-for="(option, optIndex) in field.options"
                        :key="optIndex"
                        close
                        @click:close="removeOption(field, optIndex)"
                      >
                        {{ option }}
                      </v-chip>
                    </v-chip-group>
                  </template>

                  <v-btn
                    icon
                    color="error"
                    class="float-right"
                    @click="removeField(index)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
                <template v-else>
                  <!-- User Answer Form -->
                  <v-row>
                    <v-col cols="12">
                      <h3 class="subtitle-1">{{ field.name }}</h3>
                      <p class="caption grey--text">{{ field.description }}</p>

                      <!-- Text Input -->
                      <v-text-field
                        v-if="field.field_type === 'Text'"
                        v-model="answers[field.id]"
                        :label="field.name"
                        :rules="field.required ? [v => !!v || 'Este campo é obrigatório'] : []"
                      />

                      <!-- Number Input -->
                      <v-text-field
                        v-if="field.field_type === 'Number'"
                        v-model.number="answers[field.id]"
                        type="number"
                        :label="field.name"
                        :rules="field.required ? [v => !!v || 'Este campo é obrigatório'] : []"
                      />

                      <!-- Single Choice -->
                      <v-radio-group
                        v-if="field.field_type === 'Choice'"
                        v-model="answers[field.id]"
                        :rules="field.required ? [v => !!v || 'Este campo é obrigatório'] : []"
                      >
                        <v-radio
                          v-for="option in field.options"
                          :key="option"
                          :label="option"
                          :value="option"
                        />
                      </v-radio-group>

                      <!-- Multiple Choice -->
                      <template v-if="field.field_type === 'MultipleChoice'">
                        <v-checkbox
                          v-for="option in field.options"
                          :key="option"
                          v-model="answers[field.id]"
                          :value="option"
                          :label="option"
                          :rules="field.required ? [v => v.length > 0 || 
                          'Este campo é obrigatório'] : []"
                        />
                      </template>

                      <!-- Date Input -->
                      <v-menu
                        v-if="field.field_type === 'Date'"
                        v-model="dateMenus[field.id]"
                        :close-on-content-click="false"
                        transition="scale-transition"
                        offset-y
                        min-width="290px"
                      >
                        <template #activator="{ on }">
                          <v-text-field
                            v-model="answers[field.id]"
                            :label="field.name"
                            :rules="field.required ? [v => !!v || 'Este campo é obrigatório'] : []"
                            readonly
                            v-on="on"
                          />
                        </template>
                        <v-date-picker
                          v-model="answers[field.id]"
                          @input="dateMenus[field.id] = false"
                        />
                      </v-menu>
                    </v-col>
                  </v-row>
                </template>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn
        text
        @click="$emit('cancel')"
      >
        Cancelar
      </v-btn>
      <v-btn
        color="primary"
        :disabled="!valid"
        @click="save"
      >
        Guardar
      </v-btn>
    </v-card-actions>

    <!-- Alert -->
    <v-snackbar
      v-model="showAlert"
      :color="alertColor"
      timeout="5000"
    >
      {{ alertMessage }}
    </v-snackbar>
  </v-card>
</template>

<script>
export default {
  name: 'PerspectiveForm',

  props: {
    projectId: {
      type: Number,
      required: true
    },
    isAdmin: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      valid: true,
      perspective: {
        is_required: true
      },
      fields: [],
      answers: {},
      dateMenus: {},
      newOption: {},
      showAlert: false,
      alertMessage: '',
      alertColor: 'success',
      fieldTypes: [
        { text: 'Texto', value: 'Text' },
        { text: 'Número', value: 'Number' },
        { text: 'Escolha Única', value: 'Choice' },
        { text: 'Escolha Múltipla', value: 'MultipleChoice' },
        { text: 'Data', value: 'Date' }
      ]
    }
  },

  async created() {
    await this.loadPerspective()
  },

  methods: {
    async loadPerspective() {
      try {
        if (this.isAdmin) {
          const response = await this.$axios.$get(`/projects/${this.projectId}/perspective`)
          this.perspective = response
          this.fields = response.fields || []
        } else {
          const response = await this.$axios.$get(`/projects/${this.projectId}/perspective/my-answers`)
          this.fields = response.fields
          this.fields.forEach(field => {
            if (field.answer !== null) {
              this.answers[field.id] = field.answer
            } else if (field.field_type === 'MultipleChoice') {
              this.answers[field.id] = []
            }
          })
        }
      } catch (error) {
        this.showError('Erro ao carregar perspetiva')
      }
    },

    addField() {
      this.fields.push({
        name: '',
        description: '',
        field_type: 'Text',
        required: true,
        options: []
      })
    },

    removeField(index) {
      this.fields.splice(index, 1)
    },

    addOption(field) {
      const option = this.newOption[field.id || field]
      if (option && option.trim()) {
        if (!field.options) {
          field.options = []
        }
        field.options.push(option.trim())
        this.newOption[field.id || field] = ''
      }
    },

    removeOption(field, index) {
      field.options.splice(index, 1)
    },

    async save() {
      if (!this.$refs.form.validate()) {
        return
      }

      try {
        if (this.isAdmin) {
          await this.$axios.$put(`/projects/${this.projectId}/perspective`, {
            is_required: this.perspective.is_required,
            fields: this.fields
          })
          this.showSuccess('Perspetiva configurada com sucesso')
        } else {
          const answers = Object.entries(this.answers).map(([field, value]) => ({
            field: parseInt(field),
            value
          }))
          
          await this.$axios.$post(`/projects/${this.projectId}/perspective/my-answers`, {
            answers
          })
          this.showSuccess('Perspetiva pessoal guardada com sucesso')
        }
        
        this.$emit('saved')
      } catch (error) {
        this.showError('Erro ao guardar perspetiva')
      }
    },

    showSuccess(message) {
      this.alertMessage = message
      this.alertColor = 'success'
      this.showAlert = true
    },

    showError(message) {
      this.alertMessage = message
      this.alertColor = 'error'
      this.showAlert = true
    }
  }
}
</script> 