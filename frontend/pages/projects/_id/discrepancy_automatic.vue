<template>
  <v-container class="mt-12">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>Sinalizar Discrepâncias Automáticas</span>
        <v-spacer />
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
          :mode="'discrepancias'"
          :display-discrepancy-as-text="true"   
        />
      </v-card-text>

      <!-- limiar -->
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
    threshold() {
      this.loadExamples()
    }
  },
  async created() {
    await this.loadExamples()
  },
  methods: {
    async loadExamples() {
      this.loading = true
      try {
        const projectId = this.$route.params.id
        const { items } = await this.$services.example.list(projectId, {})
        this.examples = items
          .filter((ex: any) => ex.is_finished)
          .map((ex: any) => {
            const dist = Object.fromEntries(
              Object.entries(ex.label_distribution || {}).map(([l, v]) => {
                const p = Number(v)
                return [l, (p > 1 ? p : p * 100).toFixed(2)]
              })
            )
            const max = Math.max(...Object.values(dist).map(Number), 0)
            const auto = max < 100 && max > this.threshold
            return {
              ...ex,
              label_distribution: dist,
              has_discrepancy: auto              // usado no DocumentList
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
