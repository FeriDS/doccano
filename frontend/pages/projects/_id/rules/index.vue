<template>
  <v-container class="pa-5 mt-16">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Regras de Anotação</span>
        <div>
          <v-btn 
            color="primary" 
            class="mr-2"
            @click="goToCreate"
          >
            Nova Regra
          </v-btn>
          <v-btn 
            color="secondary"
            @click="goToClosed"
          >
            Votações Encerradas
          </v-btn>
        </div>
      </v-card-title>

      <v-card-text>
        <v-alert v-if="error" type="error" dense class="mb-4">
          {{ error }}
        </v-alert>

        <v-progress-circular v-if="loading" indeterminate class="ma-4" />

        <v-data-table
          v-if="openRules.length"
          :headers="headers"
          :items="openRules"
          item-key="id"
          class="elevation-1 mt-4"
        >
          <template #[`item.votes_yes`]="{ item }">
            {{ item.votes_yes }}
          </template>

          <template #[`item.votes_no`]="{ item }">
            {{ item.votes_no }}
          </template>

          <template #[`item.action`]="{ item }">
            <div class="d-flex">
              <v-avatar
              v-if="item.vote === true"
                size="40"
                color="green lighten-4"
                class="mr-2"
              >
                <v-btn
                  icon
                  depressed
                  :disabled="!item.is_open"
                  color="green darken-2"
                  class="text-white"
                  @click="onVote(item.id, true)"
                >
                  👍
                </v-btn>
              </v-avatar>

              <v-btn
                v-else
                icon
                depressed
                :disabled="!item.is_open"
                :color="item.vote === false ? 'grey lighten-1' : 'green lighten-4'"
                :class="item.vote === false ? 'text--secondary' : 'text--secondary'"
                @click="onVote(item.id, true)"
              >
                👍
              </v-btn>

              <v-avatar
              v-if="item.vote === false"
                size="40"
                color="red lighten-4"
                class="ml-2"
              >
                <v-btn
                  icon
                  depressed
                  :disabled="!item.is_open"
                  color="red darken-2"
                  class="text-white"
                  @click="onVote(item.id, false)"
                >
                  👎
                </v-btn>
              </v-avatar>

              <v-btn
                v-else
                icon
                depressed
                :disabled="!item.is_open"
                :color="item.vote === true ? 'grey lighten-1' : 'red lighten-4'"
                :class="item.vote === true ? 'text--secondary' : 'text--secondary'"
                class="ml-2"
                @click="onVote(item.id, false)"
              >
                👎
              </v-btn>
            </div>
          </template>

          <template #[`item.close`]="{ item }">
            <v-btn
              small
              color="warning"
              @click="closeVoting(item.id)"
            >
              Encerrar
            </v-btn>
          </template>
        </v-data-table>

        <div v-if="!loading && !openRules.length" class="text-gray-600 mt-4">
          Nenhuma regra disponível para votação neste momento.
        </div>

        <v-snackbar v-model="snackbar" top :color="snackbarColor" :timeout="3000">
          {{ snackbarMessage }}
        </v-snackbar>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
export default {
  async asyncData({ params, $axios, error }) {
    try {
      // 1. Busca dados do projeto
      const project = await $axios.$get(`/api/projects/${params.id}`)
      
      // 2. Busca regras do projeto
      const rules = await $axios.$get(`/api/projects/${params.id}/rules`)
      
      return {
        projectId: params.id,
        project,
        rules
      }
    } catch (err) {
      error({
        statusCode: err.response?.status || 500,
        message: err.message
      })
    }
  }
}
</script>