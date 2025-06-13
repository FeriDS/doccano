<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h4 mb-4">Create Profile</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card class="pa-4">
          <v-form ref="form" v-model="valid" @submit.prevent="submitForm">
            <v-text-field
              v-model="form.name"
              label="Nome do Perfil"
              :rules="[rules.required]"
              required
            ></v-text-field>

            <v-textarea
              v-model="form.description"
              label="Descrição"
              :rules="[rules.required]"
              required
            ></v-textarea>

            <v-select
              v-model="form.permissions"
              :items="availablePermissions"
              item-value="id"
              item-text="name"
              label="Permissões"
              multiple
              chips
              :rules="[rules.required]"
            >
              <template #selection="{ item }">
                <v-chip>
                  <v-icon left>{{ mdiShield }}</v-icon>
                  {{ item.name }}
                </v-chip>
              </template>
            </v-select>

            <div class="d-flex justify-space-between mt-4">
              <v-btn
                color="primary"
                type="submit"
                :loading="loading"
                :disabled="!valid"
              >
                Create Profile
              </v-btn>

              <v-btn
                text
                @click="$router.push('/profiles/index')"
              >
                Cancel
              </v-btn>
            </div>
          </v-form>
        </v-card>
      </v-col>
    </v-row>

    <!-- Alerta de erro discreto -->
    <v-row v-if="showErrorAlert" justify="center">
      <v-col cols="12" md="8">
        <v-alert
          type="error"
          class="mb-4 text-center"
          border="left"
          prominent
          dismissible
          @input="showErrorAlert = false"
        >
          <span style="font-size: 1.1rem;">{{ snackbarText }}</span>
        </v-alert>
      </v-col>
    </v-row>
    <!-- Snackbar de sucesso -->
    <v-snackbar
      v-model="showSnackbar"
      :color="snackbarColor"
      timeout="3000"
      v-if="snackbarColor === 'success'"
    >
      {{ snackbarText }}
    </v-snackbar>
  </v-container>
</template>

<script lang="ts">
import { mdiShield } from '@mdi/js'
import Vue from 'vue'
import axios from 'axios'

interface FormData {
  name: string
  description: string
  permissions: number[]
}

interface ValidationRules {
  required: (v: any) => boolean | string
}

export default Vue.extend({
  data() {
    return {
      mdiShield,
      valid: false,
      loading: false,
      showSnackbar: false,
      showErrorDialog: false,
      showErrorAlert: false,
      snackbarText: '',
      snackbarColor: 'success',
      form: {
        name: '',
        description: '',
        permissions: [] as number[]
      } as FormData,
      rules: {
        required: (v: any) => !!v || 'Campo obrigatório'
      } as ValidationRules,
      availablePermissions: [] as { id: number, name: string }[]
    }
  },

  created() {
    this.fetchPermissions()
  },

  methods: {
    async fetchPermissions() {
      try {
        const response = await axios.get('/v1/permissions/')
        this.availablePermissions = response.data
      } catch (e) {
        this.availablePermissions = []
      }
    },

    async submitForm() {
      const form = this.$refs.form as Vue & { validate: () => boolean }
      if (!form.validate()) return

      this.loading = true
      try {
        console.log('Enviando dados do perfil:', this.form)
        const response = await this.$repositories.profile.create(this.form)
        console.log('Resposta do servidor:', response)
        this.snackbarText = 'Perfil criado com sucesso'
        this.snackbarColor = 'success'
        this.showSnackbar = true
        this.$router.push('/profiles')
      } catch (error: any) {
        console.error('Erro ao criar perfil:', error)
        console.error('Detalhes do erro:', error.response?.data)
        this.snackbarText = error.response?.data?.detail || error.response?.data?.error || 'Erro ao criar perfil'
        this.snackbarColor = 'error'
        this.showErrorAlert = true
      } finally {
        this.loading = false
      }
    }
  }
})
</script> 