<template>
  <v-container class="mt-12">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>Sinalizar Discrepâncias</span>
        <v-spacer />
        <v-btn color="primary" class="mr-2" @click="onShowAnnotation"
        :disabled="!canShowAnnotation">
          Show Annotation
        </v-btn>
        <v-btn text aria-label="Return" @click="$router.back()">
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </v-card-title>

      <v-card-text>
        <document-list
          v-model="selected"
          :items="examples"
          :is-loading="loading"
          :is-admin="true"
          :total="total"
          :members="members"
          mode="discrepancias"
          @discrepancy-change="onDiscrepancyChange"
        />
      </v-card-text>
    </v-card>

    <!-- diálogo de confirmação -->
    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card>
        <v-card-title class="headline">
          Are you sure you want to change the discrepancy status?
        </v-card-title>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="confirmDiscrepancyChange">Confirm</v-btn>
          <v-btn color="grey" @click="cancelDiscrepancyChange">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiArrowLeft } from '@mdi/js'
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
      mdiArrowLeft
    }
  },
  async created() {
    await this.fetchExamples()
  },
  computed: {
  canShowAnnotation(): boolean {
    if (!Array.isArray(this.selected) || this.selected.length === 0) return false

    // Se selected contém objetos completos
    if (typeof this.selected[0] === 'object') {
      return this.selected.some((ex: any) => ex.has_discrepancy)
    }

    // Se selected contém apenas IDs
    return this.selected
      .map((id: any) => this.examples.find((ex: any) => ex.id === id))
      .some((ex: any) => ex && ex.has_discrepancy)
  }
},
  methods: {
   onShowAnnotation() {
  // Supondo que só um exemplo pode ser selecionado:
  const selectedId = Array.isArray(this.selected) ? this.selected[0] : this.selected
  const link = this.localePath({
    path: `/projects/${this.$route.params.id}/annotations`,
    query: { example: selectedId }
  })
  this.$router.push(link)
},

    /* ---------- dados ---------- */
    async fetchExamples() {
      this.loading = true
      try {
        const { id } = this.$route.params
        const { items } = await this.$services.example.list(id, {})
        this.examples = items
          .filter((it: any) => it.is_finished)
          .map((it: any) => ({
            ...it,
            label_distribution: Object.fromEntries(
              Object.entries(it.label_distribution || {}).map(([l, v]) => {
                const p = Number(v)
                return [l, (p > 1 ? p : p * 100).toFixed(2)]
              })
            )
          }))
        this.total = this.examples.length
      } finally {
        this.loading = false
      }
    },

    /* ---------- discrepância ---------- */
    onDiscrepancyChange(example: any) {
      this.pendingDiscrepancy = example
      this.confirmDialog = true
    },
    async confirmDiscrepancyChange() {
      const projectId = this.$route.params.id
      const ex = this.pendingDiscrepancy
      await this.$services.example.update(projectId, {
        id: ex.id,
        has_discrepancy: ex.has_discrepancy
      })
      await this.fetchExamples()
      this.confirmDialog = false
      this.pendingDiscrepancy = null
    },
    cancelDiscrepancyChange() {
      if (this.pendingDiscrepancy) {
        this.pendingDiscrepancy.has_discrepancy =
          !this.pendingDiscrepancy.has_discrepancy
      }
      this.confirmDialog = false
      this.pendingDiscrepancy = null
    }
  }
})
</script>
