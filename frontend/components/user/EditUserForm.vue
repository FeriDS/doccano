<template>
  <v-card>
    <v-card-title>{{ isCurrentUser ? 'Edit Profile' : 'Edit User' }}</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <v-text-field
          v-model="formData.username"
          :rules="[rules.required]"
          label="Username"
          required
        />
        <v-text-field
          v-model="formData.first_name"
          label="First Name"
        />
        <v-text-field
          v-model="formData.last_name"
          label="Last Name"
        />
        <v-text-field
          v-model="formData.email"
          :rules="[rules.required, rules.email]"
          label="Email"
          required
        />
        <template v-if="showSuperUserSwitch">
          <v-switch
            v-model="formData.isSuperuser"
            label="Superuser Permissions"
            hint="Grants full access to the system"
            persistent-hint
          />
        </template>
        <v-alert
          v-if="isCurrentUser && user.isSuperuser"
          type="info"
          class="mt-4 mb-4"
          border="left"
          dense
        >
          Superuser permissions cannot be modified on your own profile.
        </v-alert>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn
        color="primary"
        :disabled="!valid"
        @click="save"
      >
        Save
      </v-btn>
      <v-btn
        text
        @click="cancel"
      >
        Cancel
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { UserItem } from '@/domain/models/user/user'

export default Vue.extend({
  props: {
    user: {
      type: Object as () => UserItem,
      required: true
    },
    isAdmin: {
      type: Boolean,
      required: true
    }
  },

  data() {
    return {
      valid: false,
      formData: {
        username: this.user.username,
        first_name: this.user.first_name || '',
        last_name: this.user.last_name || '',
        email: this.user.email,
        isSuperuser: this.user.isSuperuser
      },
      rules: {
        required: (v: string) => !!v || 'Este campo é obrigatório',
        email: (v: string) => /.+@.+\..+/.test(v) || 'Email deve ser válido'
      },
      otherAdminExists: false
    }
  },

  computed: {
    isCurrentUser(): boolean {
      const currentUserId = this.$store.getters['auth/userId']
      return this.user.id === currentUserId
    },

    showSuperUserSwitch(): boolean {
      // Only show the switch if:
      // 1. User has admin permissions (isAdmin)
      // 2. Not editing their own profile
      return this.isAdmin && !this.isCurrentUser
    }
  },

  watch: {
    'formData.isSuperuser'(newValue: boolean) {
      // If current user tries to remove their own superuser status, prevent it and reset the switch
      if (this.isCurrentUser && this.user.isSuperuser && !newValue) {
        // Reset the switch back to true
        this.$nextTick(() => {
          this.formData.isSuperuser = true
        })
        this.$store.dispatch('snackbar/error', 'Você não pode remover suas próprias permissões de superutilizador.')
      }
    }
  },

  async created() {
    try {
      const users = await this.$repositories.user.list('')
      // Verifica se existe outro admin além do usuário atual
      this.otherAdminExists = users.some(u => 
        u.isStaff && 
        u.id !== this.user.id && 
        u.id !== this.$store.getters['auth/userId']
      )
    } catch (error) {
      console.error('Erro ao verificar outros admins:', error)
    }
  },

  mounted() {
    console.log('Component mounted:', {
      user: this.user,
      isCurrentUser: this.isCurrentUser,
      isAdmin: this.isAdmin,
      formData: this.formData,
      storeUserId: this.$store.getters['auth/userId']
    })
  },

  methods: {
    async save() {
      try {
        const dataToSend: {
          username: string
          first_name: string
          last_name: string
          email: string
          isSuperuser?: boolean
        } = {
          username: this.formData.username,
          first_name: this.formData.first_name,
          last_name: this.formData.last_name,
          email: this.formData.email
        }

        // Only include superuser status if:
        // 1. User is an admin
        // 2. Not editing their own profile
        if (this.isAdmin && !this.isCurrentUser) {
          dataToSend.isSuperuser = this.formData.isSuperuser
        }

        await this.$repositories.user.updateUser(this.user.id, dataToSend)
        this.$emit('saved')
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || 
                           error.response?.data?.error || 
                           'Erro ao atualizar utilizador'
        this.$store.dispatch('snackbar/error', errorMessage)
      }
    },

    cancel() {
      this.$emit('cancel')
    }
  }
})
</script> 