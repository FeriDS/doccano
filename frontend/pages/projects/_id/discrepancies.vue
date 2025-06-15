<template>
  <v-container class="mt-12">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>Sinalizar Discrepâncias</span>
        <v-spacer />
        <v-btn color="primary" class="mr-2" @click="onShowAnnotation">
          Show Annotation
        </v-btn>
        <v-btn text aria-label="Return" @click="$router.back()">
          <v-icon left>{{ mdiArrowLeft }}</v-icon>
          Return
        </v-btn>
      </v-card-title>

      <v-card-text>
        <document-list
          :items="examples"
          :is-loading="loading"
          :is-admin="true"
          :total="total"
          :members="members"
          :value="selected"
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
  methods: {
    /* rota SEM query selected */
    onShowAnnotation() {
      const link = this.localePath(`/projects/${this.$route.params.id}/annotations`)
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
