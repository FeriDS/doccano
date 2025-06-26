<!-- eslint-disable vue/valid-v-slot -->
<template>
  <v-container class="mt-12">
    <v-card>
      <!-- ───────────── Header ───────────── -->
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

      <!-- ───────────── Table ────────────── -->
      <v-card-text>
        <v-data-table
          :items="examples"
          :headers="headers"
          :loading="loading"
          item-key="id"
          :footer-props="{ 'items-per-page-options': [10, 50, 100] }"
        >
          <!-- TEXT --------------------------------------------------- -->
          <template #[`item.text`]="{ item }">
            <span class="d-flex d-sm-none">
              {{ item.text.length > 50 ? item.text.slice(0, 50) + '…' : item.text }}
            </span>
            <span class="d-none d-sm-flex">
              {{ item.text.length > 200 ? item.text.slice(0, 200) + '…' : item.text }}
            </span>
          </template>

          <!-- LABEL DISTRIBUTION ------------------------------------ -->
          <template #[`item.label_distribution`]="{ item }">
            <div>
              <v-chip
                v-for="(percent, label) in item.label_distribution"
                :key="'dist-' + label"
                small
                class="ma-1"
              >
                {{ label }}: {{ percent }}%
              </v-chip>
            </div>
          </template>

          <!-- DISCREPANCY STATUS ------------------------------------ -->
          <template #[`item.has_discrepancy`]="{ item }">
            <!-- TRUE  ⇒ cruz vermelha -->
            <template v-if="item.has_discrepancy">
              <v-icon color="error" small>{{ mdiClose }}</v-icon>
              <span class="ml-1 error--text">Has Discrepancy</span>
            </template>

            <!-- FALSE ⇒ verde + label(s) principal(ais) -->
            <template v-else>
              <v-icon color="success" small class="mr-1">{{ mdiCheck }}</v-icon>
              <span class="success--text font-weight-medium">
                No discrepancy, majority agreed on :
              </span>

              <!-- cada lbl gera DOIS chips; wrapper precisa de key real -->
              <span
                v-for="lbl in item.top_labels"
                :key="'lblwrap-' + lbl"
                class="d-inline-flex"
              >
                <v-chip
                  color="primary"
                  small
                  class="ma-1 white--text"
                  :key="'lbl-' + lbl"
                >
                  {{ lbl }}
                </v-chip>

                <v-chip
                  color="primary"
                  small
                  class="ma-1 white--text"
                  :key="'pct-' + lbl"
                >
                  {{ item.label_distribution[lbl] }}%
                </v-chip>
              </span>
            </template>
          </template>
        </v-data-table>
      </v-card-text>

      <!-- ───────────── Threshold ────────── -->
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
import { mdiArrowLeft, mdiClose, mdiCheck } from '@mdi/js'
import { ExampleDTO } from '~/services/application/example/exampleData'

export default Vue.extend({
  data() {
    return {
      examples : [] as ExampleDTO[],
      loading  : false,
      total    : 0,
      threshold: 75,
      mdiArrowLeft, mdiClose, mdiCheck
    }
  },

  computed: {
    headers(): any[] {
      return [
        { text: this.$t('dataset.text'),            value: 'text',               sortable: false },
        { text: this.$t('dataset.labelDistribution') || 'Label Distribution',
          value: 'label_distribution', sortable: false },
        { text: 'Discrepancy', value: 'has_discrepancy', sortable: false }
      ]
    }
  },

  watch: {
    threshold(val: number) {
      if (process.client) localStorage.setItem('discrepancyThreshold', String(val))
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
      this.$router.push(
        this.localePath(`/projects/${this.$route.params.id}/annotations`)
      )
    },

    /** carrega exemplos + cálculo de status/top_labels */
    async loadExamples() {
      this.loading = true
      try {
        const { items } = await this.$services.example.list(this.$route.params.id, {})

        this.examples = items
          .filter((ex: any) => ex.is_finished)
          .map((ex: any) => {
            /* distribuição em % (2 casas) */
            const raw = Object.entries(ex.label_distribution || {})
            const dist = Object.fromEntries(
              raw.map(([l, v]) => {
                const num = Number(v)
                return [l, (num > 1 ? num : num * 100).toFixed(2)]
              })
            )

            /* maior percentagem + empates */
            const percentages = raw.map(([, v]) => {
              const num = Number(v)
              return num > 1 ? num : num * 100
            })
            const maxP = percentages.length ? Math.max(...percentages) : 0
            const top_labels = raw
              .filter(([, v]) => {
                const num = Number(v)
                return (num > 1 ? num : num * 100) === maxP
              })
              .map(([l]) => l)

            const hasDisc = maxP < this.threshold

            return {
              ...ex,
              label_distribution: dist,
              has_discrepancy   : hasDisc,
              top_labels
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
.v-card { position: relative; padding-bottom: 70px; }
.threshold-input-bottom-left {
  position: absolute;
  bottom: 16px;
  left: 16px;
  width: 150px;
}
</style>
