<template>
  <base-card
    :disabled="!valid"
    :title="$t('user.create')"
    :agree-text="$t('user.create')"
    @agree="tryRegister"
  >
    <template #content>
      <v-form v-model="valid">
        <v-alert v-show="showError" v-model="showError" type="error" dismissible>
          {{ $t('errors.invalidUserOrPass') }}
        </v-alert>
        <v-text-field
          v-model="username"
          :rules="userNameRules($t('rules.userNameRules'))"
          :label="$t('user.username')"
          name="username"
          :prepend-icon="mdiAccount"
          type="text"
          autofocus
          @keyup.enter="tryRegister"
        />
        <v-text-field
          v-model="email"
          :rules="emailRules($t('rules.emailRules'))"
          :label="$t('user.email')"
          name="email"
          :prepend-icon="mdiAccount"
          type="text"
          autofocus
          @keyup.enter="tryRegister"
        />
        <v-text-field
          id="password1"
          v-model="password1"
          :rules="passwordRules($t('rules.passwordRules'))"
          :label="$t('user.password')"
          name="password"
          :prepend-icon="mdiLock"
          type="password"
          @keyup.enter="tryRegister"
        />
        <v-text-field
          id="password2"
          v-model="password2"
          :label="$t('user.passwordAgain')"
          name="password2"
          :prepend-icon="mdiLock"
          type="password"
          @keyup.enter="tryRegister"
        />
      </v-form>
    </template>
  </base-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiAccount, mdiLock } from '@mdi/js'
import { userNameRules, passwordRules, emailRules } from '@/rules/index'
import BaseCard from '@/components/utils/BaseCard.vue'
import { APIAuthRepository } from '@/repositories/auth/apiAuthRepository'

export default Vue.extend({
  components: {
    BaseCard
  },

  props: {
    register: {
      type: Function,
      default: () => Promise
    }
  },
  data() {
    return {
      valid: false,
      email: '',
      username: '',
      password1: '',
      password2: '',
      userNameRules,
      passwordRules,
      emailRules,
      showError: false,
      mdiAccount,
      mdiLock
    }
  },

  methods: {
    async tryRegister() {
      const api = new APIAuthRepository()
      try {
        await api.register(
          this.email,
          this.username,
          this.password1,
          this.password2
        )
        this.$router.push(this.localePath('/projects'))
      } catch {
        this.showError = true
      }
    }
  }
})
</script>
