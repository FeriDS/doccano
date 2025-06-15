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
          />
        </v-card-text>

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
          const result = await this.$services.example.list(projectId, {})
          this.examples = result.items
            .filter((item: any) => item.is_finished)
            .map((item: any) => {
              const labelDist = item.label_distribution || {}
              const dist = Object.fromEntries(
                Object.entries(labelDist).map(([label, value]) => {
                  const percent = Number(value)
                  return [label, percent > 1 ? percent : percent * 100]
                })
              )
              const max = Math.max(...Object.values(dist), 0)
              const has_discrepancy_automatica = max < 100 && max > this.threshold
              return {
                ...item,
                label_distribution: Object.fromEntries(
                  Object.entries(dist).map(([l, v]) => [l, v.toFixed(2)])
                ),
                has_discrepancy_automatica
              }
            })
          this.total = this.examples.length
          this.members = []
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
  