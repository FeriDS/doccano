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

      <h2 class="text-h6 mb-2">Fields</h2>

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
            <v-btn icon @click="removeField(index)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </div>

      <v-btn text color="primary" class="mb-4" @click="addField">
        <v-icon left>mdi-plus</v-icon> Add Field
      </v-btn>

      <v-btn color="primary" @click="submit">
        Create Perspective
      </v-btn>
    </v-form>
  </v-container>
</template>

<script>
export default {
  name: 'CreatePerspectivePage',
  data() {
    return {
      name: '',
      description: '',
      fields: []
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
