<template>
  <v-form ref="form" v-model="valid">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="formData.name"
            :label="$t('perspectives.name')"
            :rules="[v => !!v || $t('rules.required')]"
            required
          />
        </v-col>
        <v-col cols="12">
          <v-textarea
            v-model="formData.description"
            :label="$t('perspectives.description')"
            :rules="[v => !!v || $t('rules.required')]"
            required
          />
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <v-row>
        <v-col cols="12">
          <h3>{{ $t('perspectives.fields') }}</h3>
          <v-btn
            color="primary"
            text
            @click="addField"
          >
            {{ $t('generic.add') }}
          </v-btn>
        </v-col>
      </v-row>

      <v-row v-for="(field, index) in formData.fields" :key="index">
        <v-col cols="12" md="3">
          <v-text-field
            v-model="field.name"
            :label="$t('perspectives.fieldName')"
            :rules="[v => !!v || $t('rules.required')]"
            required
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-textarea
            v-model="field.description"
            :label="$t('perspectives.fieldDescription')"
            :rules="[v => !!v || $t('rules.required')]"
            required
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-select
            v-model="field.field_type"
            :items="fieldTypes"
            :label="$t('perspectives.fieldType')"
            :rules="[v => !!v || $t('rules.required')]"
            required
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-switch
            v-model="field.required"
            :label="$t('perspectives.required')"
          />
        </v-col>
        <v-col cols="12" md="1">
          <v-btn
            icon
            color="error"
            @click="removeField(index)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </v-col>
        <v-col v-if="field.field_type === 'choice' || field.field_type === 'multiple'" cols="12">
          <v-combobox
            v-model="field.choices"
            :label="$t('perspectives.choices')"
            multiple
            chips
            :rules="[v => v.length > 0 || $t('rules.required')]"
            required
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" class="text-right">
          <v-btn
            color="primary"
            :disabled="!valid"
            @click="submit"
          >
            {{ $t('generic.save') }}
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="ts">
import Vue from 'vue'

interface FormData {
  name: string
  description: string
  fields: Array<{
    name: string
    description: string
    field_type: string
    required: boolean
    choices: string[]
  }>
}

export default Vue.extend({
  name: 'PerspectiveForm',

  props: {
    initialData: {
      type: Object as () => FormData,
      default: () => ({
        name: '',
        description: '',
        fields: []
      })
    }
  },

  data() {
    return {
      valid: false,
      formData: {
        name: '',
        description: '',
        fields: []
      } as FormData,
      fieldTypes: [
        { text: this.$t('perspectives.fieldTypes.text'), value: 'text' },
        { text: this.$t('perspectives.fieldTypes.number'), value: 'number' },
        { text: this.$t('perspectives.fieldTypes.boolean'), value: 'boolean' },
        { text: this.$t('perspectives.fieldTypes.choice'), value: 'choice' },
        { text: this.$t('perspectives.fieldTypes.multiple'), value: 'multiple' }
      ]
    }
  },

  watch: {
    initialData: {
      handler(newVal) {
        if (newVal) {
          this.formData = { ...newVal }
        }
      },
      immediate: true
    }
  },

  methods: {
    addField() {
      this.formData.fields.push({
        name: '',
        description: '',
        field_type: 'text',
        required: true,
        choices: []
      })
    },

    removeField(index: number) {
      this.formData.fields.splice(index, 1)
    },

    async submit() {
      if ((this.$refs.form as any).validate()) {
        await this.$nextTick()
        this.$emit('submit', this.formData)
      }
    }
  }
})
</script> 