<template>
  <v-container>
    <v-card>
      <v-card-title>
        Sinalizar Discrepâncias
      </v-card-title>
      <v-card-text>
        <document-list
          :items="examples"
          :is-loading="loading"
          :is-admin="true"
          :total="total"
          :members="members"
          :value="selected"
          :mode="'discrepancias'"
          @discrepancy-change="onDiscrepancyChange"
        />
      </v-card-text>
    </v-card>
    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card>
        <v-card-title class="headline">Are you sure you want to 
        change the discrepancy status?</v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="confirmDiscrepancyChange">Confirm</v-btn>
          <v-btn color="grey" @click="cancelDiscrepancyChange">Cancel</v-btn>
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
      pendingDiscrepancy: null as any
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