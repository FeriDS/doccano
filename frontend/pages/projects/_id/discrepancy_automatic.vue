<!-- eslint-disable vue/valid-v-slot -->
<template>
  <v-container class="mt-12">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>Automatic Discrepancies</span>
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
          mode="discrepancias"
        />
      </v-card-text>

      <!-- Threshold --------------------------------------------------- -->
      <v-text-field
        v-model.number="threshold"
        label="Threshold"
        type="number"
        min="0"
        max="100"
        dense
        suffix="%"
        class="threshold-input-bottom-left"
      />
    </v-card>
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
      threshold: 75,
      mdiArrowLeft
    }
  },
  watch: {
    threshold(newVal: number) {
      if (process.client) localStorage.setItem('discrepancyThreshold', newVal.toString())
      this.loadExamples()
    }
  },
  async created() {
    if (process.client) {
      const saved = localStorage.getItem('discrepancyThreshold')
      if (saved) this.threshold = Number(saved)
    }
    await this.loadExamples()
  },
  methods: {
    onShowAnnotation() {
      const link = this.localePath(`/projects/${this.$route.params.id}/annotations`)
      this.$router.push(link)
    },

    /** Carregar exemplos e gerar STATUS / TOP LABELS ------------------ */
    async loadExamples() {
      this.loading = true
      try {
        const projectId = this.$route.params.id
        const { items } = await this.$services.example.list(projectId, {})

        this.examples = items
          .filter((ex: any) => ex.is_finished)
          .map((ex: any) => {
            /* ---- distribuição % com 2 casas decimais --------------- */
            const rawEntries = Object.entries(ex.label_distribution || {})
            const dist = Object.fromEntries(
              rawEntries.map(([label, value]) => {
                const p = Number(value)
                return [label, (p > 1 ? p : p * 100).toFixed(2)]
              })
            )

            /* ---- maior percentagem + labels empatados ---------------- */
            const percentages = rawEntries.map(([, value]) =>
              Number(value) > 1 ? Number(value) : Number(value) * 100
            )
            const maxP = percentages.length ? Math.max(...percentages) : 0

            const topLabels = rawEntries
              .filter(([, value]) => {
                const p = Number(value) > 1 ? Number(value) : Number(value) * 100
                return p === maxP
              })
              .map(([label]) => label)

            /* ---- regra de discrepância ------------------------------ */
            const noDiscrepancy = maxP >= this.threshold

            return {
              ...ex,
              label_distribution: dist,
              has_discrepancy: !noDiscrepancy,
              status: noDiscrepancy ? 'No discrepancy' : 'Has discrepancy',
              status_color: noDiscrepancy ? 'green--text' : 'red--text',
              top_labels: topLabels
            }
          })

        this.total = this.examples.length
      } finally {
        this.loading = false
      }
    }
  }
})
</script>

<style scoped>
.v-card {
  position: relative;
  padding-bottom: 70px;
}
.threshold-input-bottom-left {
  position: absolute;
  bottom: 16px;
  left: 16px;
  width: 150px;
}
</style>
