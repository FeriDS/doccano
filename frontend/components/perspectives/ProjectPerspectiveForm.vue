<template>
  <v-form ref="form" v-model="valid" @submit.prevent="submit">
    <v-container>
      <v-row>
        <v-col cols="12" class="d-flex align-center justify-space-between">
          <h2>{{ perspective.name }}</h2>
          <v-btn
            outlined
            color="black"
            class="ml-auto"
            title="Return"
            @click="goBack"
          >
            <v-icon left color="black">mdi-arrow-left</v-icon>
            <span style="font-weight: 600; letter-spacing: 1px;">RETURN</span>
          </v-btn>
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
              :disabled="disabled"
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
              :disabled="disabled"
            />

            <!-- Boolean Field -->
            <v-switch
              v-else-if="field.field_type === 'boolean'"
              v-model="fieldValues[field.name]"
              :label="field.name"
              :hint="field.description"
              persistent-hint
              :disabled="disabled"
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
              :disabled="disabled"
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
              :disabled="disabled"
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" class="text-right d-flex justify-end align-center">
            <v-btn
              color="primary"
              :disabled="!valid || disabled"
              type="submit"
              class="mr-2"
            >
              {{ $t('generic.save') }}
            </v-btn>
            <v-btn
              color="grey darken-1"
              text
              @click="handleCancel"
            >
              <v-icon left>mdi-close</v-icon>
              Cancel
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
    },
    disabled: {
      type: Boolean,
      default: false
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
    },
    handleCancel() {
      this.fieldValues = {}
      this.$emit('cancel')
    },
    goBack() {
      this.$router.push(`/projects/${this.$route.params.id}`)
    }
  }
})
</script> 