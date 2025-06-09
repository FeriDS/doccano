<template>
  <v-container class="mt-16">
    <h1 class="text-h4 mb-4">Create Perspective</h1>

    <v-form>
      <v-text-field
        label="Name"
        v-model="name"
        required
        class="mb-4"
      />

      <v-textarea
        label="Description"
        v-model="description"
        rows="3"
        class="mb-4"
      />

      <div class="d-flex align-center mb-4">
        <h2 class="text-h6 mb-0">Fields</h2>
      </div>

      <div v-for="(field, index) in fields" :key="index" class="mb-4">
        <v-row dense>
          <v-col cols="5">
            <v-text-field
              label="Field Name"
              v-model="field.name"
              required
            />
          </v-col>
          <v-col cols="5">
            <v-select
              label="Field Type"
              :items="['text', 'number', 'boolean']"
              v-model="field.field_type"
              required
            />
          </v-col>
          <v-col cols="2" class="d-flex align-center">
            <v-btn
              icon
              color="error"
              @click="removeField(index)"
              aria-label="Delete field"
            >
              <v-icon>{{ mdiDelete }}</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </div>

      <div class="d-flex justify-start mb-4">
        <v-btn
          color="primary"
          @click="addField"
          aria-label="Add Field"
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
          @click="$router.back()"
          aria-label="Return"
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
      this.fields.push({ name: '', field_type: 'text' })
    },
    removeField(index) {
      this.fields.splice(index, 1)
    },
    submit() {
      const perspective = {
        name: this.name,
        description: this.description,
        fields: this.fields
      }
      console.log('Submitting:', perspective)
      // Aqui poderás fazer o POST para a API
    }
  }
}
</script>
