<template>
  <v-container class="mt-12">
    <v-row>
      <!-- Coluna das Anotações -->
      <v-col cols="8">
        <v-card>
          <v-card-title>
            Anotações
          </v-card-title>
          <v-card-text>
            <document-list
              :items="examples"
              :is-loading="loading"
              :is-admin="true"
              :total="total"
              :members="members"
              :value="selected"
              :mode="'annotations'"
              @select="onSelectDocument"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Coluna das Discrepâncias -->
      <v-col cols="4">
        <v-card>
          <v-card-title>
            Discrepâncias Assinaladas
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="example in examplesWithDiscrepancies"
                :key="example.id"
                @click="onSelectDocument(example)"
              >
                <v-list-item-content>
                  <v-list-item-title>
                    Documento #{{ example.id }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ example.text.substring(0, 100) }}...
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Visualização Detalhada -->
    <v-dialog
      v-model="showDetailDialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <v-card v-if="selectedDocument">
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="showDetailDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Documento #{{ selectedDocument.id }}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn
            :color="selectedDocument.has_discrepancy ? 'error' : 'success'"
            @click="onDiscrepancyChange(selectedDocument)"
          >
            {{ selectedDocument.has_discrepancy ? 
            'Remover Discrepância' : 
            'Marcar como Discrepância' }}
          </v-btn>
        </v-toolbar>

        <v-row class="mt-4">
          <v-col 
            v-for="category in selectedDocument.categories" 
            :key="category"
            :cols="12 / selectedDocument.categories.length"
          >
            <v-card class="mx-4">
              <v-card-title class="d-flex align-center">
                <span>Label: {{ category }}</span>
                <v-spacer></v-spacer>
                <v-chip
                  color="primary"
                  small
                >
                  {{ selectedDocument.label_distribution[category] || '0' }}%
                </v-chip>
              </v-card-title>
              <v-card-text>
                <div class="text-body-1">{{ selectedDocument.text }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Estado da Discrepância -->
        <v-row class="mt-4">
          <v-col cols="12">
            <v-card class="mx-4">
              <v-card-title>Estado da Discrepância</v-card-title>
              <v-card-text>
                <v-alert
                  :type="selectedDocument.has_discrepancy ? 'error' : 'success'"
                  :icon="selectedDocument.has_discrepancy ? 'mdi-alert' : 'mdi-check-circle'"
                >
                  {{ selectedDocument.has_discrepancy ? 
                  'Este documento foi marcado como tendo discrepâncias' : 
                  'Não foram marcadas discrepâncias para este documento' }}
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card>
        <v-card-title class="headline">
          Tem a certeza que pretende alterar o estado da discrepância?
        </v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="confirmDiscrepancyChange">Confirmar</v-btn>
          <v-btn color="grey" @click="cancelDiscrepancyChange">Cancelar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import DocumentList from '@/components/example/DocumentList.vue'
import { ExampleDTO } from '~/services/application/example/exampleData'

export default Vue.extend({
  components: { DocumentList },
  data() {
    return {
      examples: [] as ExampleDTO[],
      loading: false,
      total: 0,
      members: [],
      selected: [] as number[],
      confirmDialog: false,
      pendingDiscrepancy: null as any,
      selectedDocument: null as any,
      showDetailDialog: false
    }
  },
  computed: {
    examplesWithDiscrepancies() {
      return this.examples.filter(example => example.has_discrepancy)
    }
  },
  async created() {
    this.loading = true
    try {
      const projectId = this.$route.params.id
      const result = await this.$services.example.list(projectId, {})
      this.examples = result.items
        .filter((item: any) => item.is_finished)
        .map((item: any) => ({
          ...item,
          label_distribution: Object.fromEntries(
            Object.entries(item.label_distribution || {}).map(
              ([label, value]) => {
                const percent = Number(value)
                if (percent > 1) {
                  return [label, percent.toFixed(2)]
                } else {
                  return [label, (percent * 100).toFixed(2)]
                }
              }
            )
          )
        }))
      this.total = this.examples.length
      this.members = []

      // Verificar se há um documento selecionado na query
      const selectedId = this.$route.query.selected
      if (selectedId) {
        const selectedExample = this.examples.find(example => example.id.toString() === selectedId)
        if (selectedExample) {
          try {
            // Tentar obter as categorias do exemplo
            const categories = 
            await this.$services.example.getCategories(projectId, selectedExample.id)
            selectedExample.categories = categories
          } catch (error) {
            console.warn('Não foi possível obter as categorias:', error)
            // Se não conseguir obter as categorias, usar as labels como fallback
            selectedExample.categories = Object.keys(selectedExample.label_distribution || {})
          }
          this.selectedDocument = selectedExample
          this.selected = [selectedExample.id]
          this.$nextTick(() => {
            this.showDetailDialog = true
          })
        }
      }
    } finally {
      this.loading = false
    }
  },
  watch: {
    // Observar mudanças na query para atualizar a seleção
    '$route.query.selected': {
      immediate: true,
      handler(newSelectedId) {
        if (newSelectedId) {
          const selectedExample = 
          this.examples.find(example => example.id.toString() === newSelectedId)
          if (selectedExample) {
            this.selectedDocument = selectedExample
            this.selected = [selectedExample.id]
            this.$nextTick(() => {
              this.showDetailDialog = true
            })
          }
        }
      }
    }
  },
  methods: {
    onSelectDocument(example: ExampleDTO) {
      this.selectedDocument = example
      this.selected = [example.id]
      this.showDetailDialog = true
    },
    onDiscrepancyChange(example: any) {
      this.pendingDiscrepancy = example
      this.confirmDialog = true
    },
    async confirmDiscrepancyChange() {
      const projectId = this.$route.params.id
      const example = this.pendingDiscrepancy
      const payload = { has_discrepancy: example.has_discrepancy }
      await this.$services.example.update(projectId, { ...payload, id: example.id })
      const result = await this.$services.example.list(projectId, {})
      this.examples = result.items
        .filter((item: any) => item.is_finished)
        .map((item: any) => ({
          ...item,
          label_distribution: Object.fromEntries(
            Object.entries(item.label_distribution || {}).map(
              ([label, value]) => {
                const percent = Number(value)
                if (percent > 1) {
                  return [label, percent.toFixed(2)]
                } else {
                  return [label, (percent * 100).toFixed(2)]
                }
              }
            )
          )
        }))
      this.total = this.examples.length
      this.confirmDialog = false
      this.pendingDiscrepancy = null
    },
    cancelDiscrepancyChange() {
      if (this.pendingDiscrepancy) {
        this.pendingDiscrepancy.has_discrepancy = !this.pendingDiscrepancy.has_discrepancy
      }
      this.confirmDialog = false
      this.pendingDiscrepancy = null
    }
  }
})
</script>
