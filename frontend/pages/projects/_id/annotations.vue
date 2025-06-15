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
        selected: [],
        confirmDialog: false,
        pendingDiscrepancy: null as any,
        selectedDocument: null as any
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
      } finally {
        this.loading = false
      }
    },
    methods: {
      onSelectDocument(example: any) {
        this.selectedDocument = example
        this.selected = [example.id]
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