<template>
  <v-container class="pa-5 mt-16">
    <v-card>
      <v-card-title>Sinalizar anotações com discrepâncias</v-card-title>
      <v-dialog v-model="confirmDialog" max-width="400">
        <v-card>
          <v-card-title class="headline">Confirmar Sinalização</v-card-title>
          <v-card-text>Tem certeza que deseja sinalizar essa discrepância?</v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="grey" text @click="confirmDialog = false">Cancelar</v-btn>
            <v-btn color="error" text @click="confirmDiscrepancy">Confirmar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      
      <v-card-text>
        <v-alert v-if="error" type="error">{{ error }}</v-alert>
        <v-progress-circular v-if="loading" indeterminate />

        <v-data-table
          v-if="examples.length"
          :headers="headers"
          :items="examples"
          item-key="id"
          class="elevation-1 mt-4"
        >
          <template #[`item.annotations`]="{ item }">
            <div v-for="annotation in item.annotations" :key="annotation.id">
              <strong>{{ annotation.user }}:</strong> {{ annotation.label }}
            </div>
          </template>

          <template #[`item.action`]="{ item }">
           <!-- Caso: Menos de 2 anotações -->
            <v-chip
              v-if="item.annotations.length < 2"
              color="grey"
              text-color="white"
              class="ma-2"
              small
            >
              Anotações insuficientes para sinalizar discrepância
            </v-chip>

            <!-- Caso: Já foi sinalizado -->
            <v-chip
              v-else-if="item.discrepancyMarked"
              color="green"
              text-color="white"
              class="ma-2"
              small
            >
              ✅ Discrepância já sinalizada
            </v-chip>

            <!-- Caso: Pode sinalizar -->
            <v-btn
              v-else
              color="error"
              small
              @click="openConfirmation(item)"
            >
              Sinalizar discrepância
            </v-btn>
          </template>
        </v-data-table>

        <v-snackbar v-model="snackbar" top :color="snackbarColor" :timeout="3000">
          {{ snackbarMessage }}
        </v-snackbar>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { useDiscrepancy } from '@/composables/useDiscrepancy'

function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Tempo limite excedido'))
    }, ms)

    promise
      .then((value) => {
        clearTimeout(timer)
        resolve(value)
      })
      .catch((err) => {
        clearTimeout(timer)
        reject(err)
      })
  })
}

export default Vue.extend({
  data() {
    return {
      examples: [] as any[],
      loading: false,
      error: '',
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success',
      confirmDialog: false,
      selectedExample: null as any,
      headers: [
        { text: 'Texto', value: 'text' },
        { text: 'Anotações', value: 'annotations' },
        { text: 'Ação', value: 'action', sortable: false }
      ]
      
    }
  },

  created() {
    this.fetchExamples()
  },

  
 // async created() {
   

  methods: {
    async fetchExamples() {
      const projectId = parseInt(this.$route.params.id)
      this.loading = true
        
      const { fetchExamplesWithAnnotations } = useDiscrepancy()

      try {
        this.examples = await withTimeout(fetchExamplesWithAnnotations(projectId), 5000)
      } catch (err : any) {
        if (!err.response || err.message === 'Network Error' || err.message === 'Tempo limite excedido') {
          this.error = 'Erro de ligação com base de dados. Por favor tente mais tarde.'
        } else {
          this.error = 'Erro ao carregar exemplos com anotações.'
        }
      } finally {
        this.loading = false
      }
    },
    openConfirmation(example: any) {
      this.selectedExample = example
      this.confirmDialog = true
    },
    async confirmDiscrepancy() {
      if (this.selectedExample) {
        await this.handleDiscrepancy(this.selectedExample)
        this.confirmDialog = false
      }
    },

    async handleDiscrepancy(example: any) {
    const projectId = parseInt(this.$route.params.id)
    try {
      const { markDiscrepancy } = useDiscrepancy()
      await withTimeout(markDiscrepancy(projectId, example.id), 3000)

      example.discrepancyMarked = true

      this.snackbarMessage = 'Discrepância sinalizada com sucesso.'
      this.snackbarColor = 'success'

    } catch (err : any) {
        if (!err.response || err.message === 'Network Error' || err.message === 'Tempo limite excedido') {
        this.snackbarMessage = 'Erro de ligação com base de dados. Por favor tente mais tarde.'
      } else {
        this.snackbarMessage = 'Erro ao sinalizar discrepância.'
      }
      this.snackbarColor = 'error'
    }
    this.snackbar = true
  }
  }
})
</script>
