<template>
  <v-container class="mt-16">
    <h1 class="text-h4 mb-4">Create Perspective</h1>

    <v-form>
      <v-text-field
        v-model="name"
        label="Name"
        required
        class="mb-4"
      />

      <v-textarea
        v-model="description"
        label="Description"
        rows="3"
        class="mb-4"
      />

      <div class="d-flex align-center mb-4">
        <h2 class="text-h6 mb-0">Fields</h2>
      </div>

      <div v-for="(field, index) in fields" :key="index" class="mb-4">
        <v-row dense>
          <v-col cols="4">
            <v-text-field
              v-model="field.name"
              label="Field Name"
              required
            />
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="field.description"
              label="Field Description"
              required
            />
          </v-col>
          <v-col cols="3">
            <v-select
              v-model="field.field_type"
              label="Field Type"
              :items="['text', 'number', 'boolean', 'choice', 'multiple']"
              required
            />
          </v-col>
          <v-col cols="1" class="d-flex align-center">
            <v-btn
              icon
              color="error"
              aria-label="Delete field"
              @click="removeField(index)"
            >
              <v-icon>{{ mdiDelete }}</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        <v-row v-if="field.field_type === 'choice' || field.field_type === 'multiple'" dense>
          <v-col cols="12">
            <v-combobox
              v-model="field.choices"
              label="Choices"
              multiple
              chips
              small-chips
              deletable-chips
              required
            />
          </v-col>
        </v-row>
      </div>

      <div class="d-flex justify-start mb-4">
        <v-btn
          color="primary"
          aria-label="Add Field"
          @click="addField"
        >
          <v-icon left>{{ mdiPlus }}</v-icon>
          Add Field
        </v-btn>
      </div>

      <div class="d-flex justify-space-between">
        <v-btn color="success" @click="submit">
          Create Perspective
        </v-btn>
        <v-btn
          text
          aria-label="Return"
          @click="$router.back()"
        >
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </div>
    </v-form>
  </v-container>
</template>

<script>
import { mdiArrowLeft, mdiPlus, mdiDelete } from '@mdi/js'

export default {
  name: 'CreatePerspectivePage',
  data() {
    return {
      name: '',
      description: '',
      fields: [],
      mdiArrowLeft,
      mdiPlus,
      mdiDelete
    }
  },
  methods: {
    addField() {
      this.fields.push({
        name: '',
        description: '',
        field_type: 'text',
        required: true,
        choices: []
      })
    },
    removeField(index) {
      this.fields.splice(index, 1)
    },
    submit() {
      // Validate required fields
      if (!this.name || !this.description) {
        this.$store.dispatch('snackbar/show', {
          text: this.$t('rules.required').toString(),
          color: 'error'
        })
        return
      }

      // Validate fields
      const invalidFields = this.fields.filter(field => {
        if (!field.name || !field.description) return true
        if ((field.field_type === 'choice' || field.field_type === 'multiple') && (!field.choices || field.choices.length === 0)) return true
        return false
      })

      if (invalidFields.length > 0) {
        this.$store.dispatch('snackbar/show', {
          text: this.$t('perspectives.invalidFields').toString(),
          color: 'error'
        })
        return
      }

      const perspective = {
        name: this.name,
        description: this.description,
        fields: this.fields.map(field => ({
          name: field.name,
          description: field.description || '',
          field_type: field.field_type,
          required: field.required || true,
          choices: field.field_type === 'choice' || field.field_type === 'multiple' ? field.choices || [] : null
        }))
      }
      
      this.$store.dispatch('perspectives/createPerspective', perspective)
        .then(() => {
          // Redirect with success message
          this.$router.push({
            path: this.localePath('/perspectives'),
            query: { 
              message: this.$t('perspectives.created').toString(),
              type: 'success'
            }
          })
        })
        .catch((error) => {
          let errorMessage = this.$t('generic.error').toString()
          if (error.response && error.response.data) {
            // Try to get detailed error message from response
            const data = error.response.data
            if (typeof data === 'object') {
              const messages = Object.entries(data)
                .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                .join('\n')
              errorMessage = messages
            } else if (typeof data === 'string') {
              errorMessage = data
            }
          }
          this.$store.dispatch('snackbar/show', {
            text: errorMessage,
            color: 'error',
            timeout: 5000,
            closable: true
          })
        })
    }
  }
}
</script>
