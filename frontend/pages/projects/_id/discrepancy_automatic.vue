<template>
  <v-container class="mt-12">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>Sinalizar Discrepâncias Automáticas</span>
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
          display-discrepancy-as-text
        />
      </v-card-text>

      <!-- Threshold -->
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
    /* rota SEM query selected */
    onShowAnnotation() {
      const link = this.localePath(`/projects/${this.$route.params.id}/annotations`)
      this.$router.push(link)
    },

    async loadExamples() {
      this.loading = true
      try {
        const projectId = this.$route.params.id
        const { items } = await this.$services.example.list(projectId, {})
        this.examples = items
          .filter((ex: any) => ex.is_finished)
          .map((ex: any) => {
            /* converter valores para % */
            const rawEntries = Object.entries(ex.label_distribution || {})
            const dist = Object.fromEntries(
              rawEntries.map(([label, value]) => {
                const p = Number(value)
                return [label, (p > 1 ? p : p * 100).toFixed(2)]
              })
            )

            /* discrepância automática:
               - deve existir distribuição
               - TODOS os percentuais <= threshold
            */
            const auto =
              rawEntries.length > 0 &&
              rawEntries
                .map(([, value]) => {
                  const p = Number(value)
                  return p > 1 ? p : p * 100
                })
                .every(p => p <= this.threshold)

            let mainLabel = ''
            if (!auto && rawEntries.length > 0) {
              const [label] = rawEntries.reduce((max, current) => {
                return Number(current[1]) > Number(max[1]) ? current : max
              }, rawEntries[0])
              mainLabel = label
            }

            return {
              ...ex,
              label_distribution: dist,
              has_discrepancy: auto,
              main_label: mainLabel
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
