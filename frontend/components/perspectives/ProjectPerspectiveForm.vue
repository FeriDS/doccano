<template>
  <v-form ref="form" v-model="valid" @submit.prevent="submit">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h2>{{ perspective.name }}</h2>
          <p class="text--secondary">{{ perspective.description }}</p>
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <template v-if="perspective.fields">
        <v-row v-for="field in perspective.fields" :key="field.id">
          <v-col cols="12">
            <!-- Text Field -->
            <v-text-field
              v-if="field.field_type === 'text'"
              v-model="fieldValues[field.name]"
              :label="field.name"
              :hint="field.description"
              persistent-hint
              :rules="field.required ? [v => !!v || 'Required'] : []"
              :required="field.required"
            />

            <!-- Number Field -->
            <v-text-field
              v-else-if="field.field_type === 'number'"
              v-model.number="fieldValues[field.name]"
              type="number"
              :label="field.name"
              :hint="field.description"
              persistent-hint
              :rules="field.required ? [v => (v !== null && v !== undefined && v !== '') 
              || 'Required'] : []"
              :required="field.required"
            />

            <!-- Boolean Field -->
            <v-switch
              v-else-if="field.field_type === 'boolean'"
              v-model="fieldValues[field.name]"
              :label="field.name"
              :hint="field.description"
              persistent-hint
            />

            <!-- Single Choice Field -->
            <v-select
              v-else-if="field.field_type === 'choice'"
              v-model="fieldValues[field.name]"
              :items="field.choices"
              :label="field.name"
              :hint="field.description"
              persistent-hint
              :rules="field.required ? [v => !!v || 'Required'] : []"
              :required="field.required"
            />

            <!-- Multiple Choice Field -->
            <v-select
              v-else-if="field.field_type === 'multiple'"
              v-model="fieldValues[field.name]"
              :items="field.choices"
              :label="field.name"
              :hint="field.description"
              persistent-hint
              multiple
              chips
              :rules="field.required ? [v => (Array.isArray(v) && v.length > 0) || 'Required'] : []"
              :required="field.required"
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" class="text-right">
            <v-btn
              color="primary"
              :disabled="!valid"
              type="submit"
            >
              {{ $t('generic.save') }}
            </v-btn>
          </v-col>
        </v-row>
      </template>

      <template v-else>
        <v-row>
          <v-col cols="12" class="text-center">
            <v-alert type="warning">
              {{ $t('perspectives.noFields') }}
            </v-alert>
          </v-col>
        </v-row>
      </template>
    </v-container>
  </v-form>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'ProjectPerspectiveForm',

  props: {
    perspective: {
      type: Object,
      required: true
    },
    initialValues: {
      type: Object,
      default: () => ({})
    }
  },

  data() {
    return {
      valid: false,
      fieldValues: {}
    }
  },

  watch: {
    initialValues: {
      handler(newVal) {
        this.fieldValues = { ...newVal }
      },
      immediate: true
    }
  },

  methods: {
    async submit() {
      if ((this.$refs.form as any).validate()) {
        await this.$nextTick()
        this.$emit('submit', this.fieldValues)
      }
    }
  }
})
</script> 