<!-- eslint-disable -->
<template>
  <v-container class="mt-12">
    <v-card>
      <!-- ───── Header ──── -->
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

      <!-- ───── Threshold ──── -->
      <v-card-text class="mb-0 pb-0">
        <div class="threshold-section">
          <div class="threshold-label mb-2">
            Insert the value of the threshold for discrepancies bellow:
          </div>
          <v-row align="center" no-gutters>
            <v-col cols="auto">
              <v-text-field
                v-model.number="threshold"
                type="number"
                min="0"
                max="100"
                dense
                suffix="%"
                class="mr-6"
                style="max-width: 150px"
              />
            </v-col>
            <v-col cols="auto">
              <v-btn color="primary" @click="onUpdateDiscrepancies">
                Update Discrepancies
              </v-btn>
            </v-col>
          </v-row>
        </div>
      </v-card-text>

      <!-- ───── Table ──── -->
      <v-card-text>
        <v-data-table
          :items="examples"
          :headers="headers"
          show-expand
          single-expand
          :loading="loading"
          item-key="id"
          :footer-props="{ 'items-per-page-options': [10, 50, 100] }"
        >
          <!-- TEXT ------------------------------------------------ -->
          <template #[`item.text`]="{ item }">
            <span class="d-flex d-sm-none">{{ truncate(item.text, 50) }}</span>
            <span class="d-none d-sm-flex">{{ truncate(item.text, 200) }}</span>
          </template>

          <!-- LABEL DISTRIBUTION  -------------------------------- -->
          <template #[`item.label_distribution`]="{ item }">
            <div>
              <v-chip
                v-for="(percent, label) in item.label_distribution"
                :key="'dist-' + label"
                class="ma-1"
                small
              >
                {{ label }}: {{ percent }}%
              </v-chip>
            </div>
          </template>

          <!-- DISCREPANCY STATUS --------------------------------- -->
          <template #[`item.has_discrepancy`]="{ item }">
            <template v-if="item.has_discrepancy">
              <v-icon color="error" small>{{ mdiClose }}</v-icon>
              <span class="ml-1 error--text">Has Discrepancy</span>
            </template>
            <template v-else>
              <v-icon color="success" small class="mr-1">{{ mdiCheck }}</v-icon>
              <span class="success--text font-weight-medium">
                No discrepancy, majority agreed on :
              </span>
              <span
                v-for="lbl in item.top_labels"
                :key="'lblwrap-' + lbl"
                class="d-inline-flex"
              >
                <v-chip :key="'lbl-' + lbl" class="ma-1 white--text" color="primary" small>
                  {{ lbl }}
                </v-chip>
                <v-chip :key="'pct-' + lbl" class="ma-1 white--text" color="primary" small>
                  {{ item.label_distribution[lbl] }}%
                </v-chip>
              </span>
            </template>
          </template>

          <!-- ═════ EXPANDED ROW ═════ -->
          <template #expanded-item="{ item }">
            <v-sheet class="pa-6" color="#fafafa" style="border-top:1px solid #e0e0e0">
              <div class="details-flex-row details-center">
                <div class="details-table-wrap">
                  <div class="subtitle-2 mb-2 text-center">Label Totals</div>
                  <v-simple-table dense class="details-table mx-auto">
                    <thead>
                      <tr><th>Label</th><th>Total Votes (%)</th></tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="([label,votes]) in Object.entries(item.label_distribution)"
                        :key="'row-' + label"
                      >
                        <td>{{ label }}</td><td>{{ votes }}</td>
                      </tr>
                    </tbody>
                  </v-simple-table>
                </div>
                <div class="details-side-text">
                  <div class="most-voted mb-3">
                    <span>Most used label :</span>
                    <v-chip class="black--text green-chip ml-2" small>
                      {{ getMostVotedLabel(item) }}
                    </v-chip>
                  </div>
                  <div class="least-voted">
                    <span>Least used label:</span>
                    <v-chip class="black--text red-chip ml-2" small>
                      {{ getLeastVotedLabel(item) }}
                    </v-chip>
                  </div>
                </div>
              </div>
            </v-sheet>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiArrowLeft, mdiClose, mdiCheck } from '@mdi/js'
import { ExampleDTO } from '~/services/application/example/exampleData'

const IGNORED = ['abstencao', 'abstenção', 'x', 'null']  // labels to ignore for stats

export default Vue.extend({
  data() {
    return {
      examples: [] as ExampleDTO[],
      loading : false,
      threshold: 75,
      mdiArrowLeft, mdiClose, mdiCheck
    }
  },

  computed: {
    headers(): any[] {
      return [
        { text: this.$t('dataset.text'), value: 'text', sortable: false },
        { text: this.$t('dataset.labelDistribution') || 'Label Distribution',
          value: 'label_distribution', sortable: false },
        { text: 'Discrepancy', value: 'has_discrepancy', sortable: false }
      ]
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
    truncate(txt: string, len:number) { return txt.length>len ? txt.slice(0,len)+'…' : txt },

    onShowAnnotation() {
      this.$router.push(this.localePath(`/projects/${this.$route.params.id}/annotations`))
    },
    onUpdateDiscrepancies() {
      if (process.client) localStorage.setItem('discrepancyThreshold', String(this.threshold))
      this.loadExamples()
    },

    /** Load + compute fields (ignoring abstencao/x) */
    async loadExamples() {
      this.loading = true
      try {
        const { items } = await this.$services.example.list(this.$route.params.id, {})
        this.examples = items
          .filter((ex:any)=>ex.is_finished)
          .map((ex:any)=>{
            const raw = Object.entries(ex.label_distribution || {})
            const dist = Object.fromEntries(
              raw.map(([l,v])=>{
                const num=Number(v)
                return [l, (num>1?num:num*100).toFixed(2)]
              })
            )

            // exclude ignored for stats
            const filteredRaw = raw.filter(
              ([l]) => !IGNORED.includes(l.toLowerCase())
            )

            const percentages = filteredRaw.map(([,v])=>Number(v)>1?Number(v):Number(v)*100)
            const maxP = percentages.length ? Math.max(...percentages) : 0

            const top_labels = filteredRaw
              .filter(([,v])=>{
                const num=Number(v)
                return (num>1?num:num*100) === maxP
              })
              .map(([l])=>l)

            return {
              ...ex,
              label_distribution: dist,
              has_discrepancy: maxP < this.threshold,
              top_labels
            }
          })
      } finally { this.loading=false }
    },

    /** helper: ignore abstencao/x */
    getMostVotedLabel(item:any) {
      const entries = Object.entries(item.label_distribution||{})
        .filter(([l])=>!IGNORED.includes(l.toLowerCase()))
      if(!entries.length) return '-'
      return entries.reduce((a,b)=>Number(a[1])>Number(b[1])?a:b)[0]
    },
    getLeastVotedLabel(item:any) {
      const entries = Object.entries(item.label_distribution||{})
        .filter(([l])=>!IGNORED.includes(l.toLowerCase()))
      if(!entries.length) return '-'
      return entries.reduce((a,b)=>Number(a[1])<Number(b[1])?a:b)[0]
    },

    getAbstencaoTotal(item:any){
      if(!item.abstencao) return 0
      return Object.values(item.abstencao).reduce((a:any,b:any)=>a+Number(b),0)
    },
    getXTotal(item:any){
      if(!item.x) return 0
      return Object.values(item.x).reduce((a:any,b:any)=>a+Number(b),0)
    }
  }
})
</script>

<style scoped>
.v-card{position:relative;padding-bottom:70px}

/* remove internal padding default in expanded content */
::v-deep .v-data-table__expanded__content{padding-left:0!important;padding-right:0!important}

/* stacked, centred */
.details-flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 32px;
  width: 100%;
}

.details-table-wrap{
  background:#fff;
  border-radius:12px;
  box-shadow:0 2px 12px rgba(0,0,0,0.07);
  padding:24px 18px;
  min-width:220px;
  max-width:320px;
}
.details-table th,.details-table td{
  text-align:center;
  padding:6px 12px;
  font-size:15px;
  white-space:nowrap;
}
.details-side-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  min-width: 140px;
  margin-left: 32px;
}
.most-voted,.least-voted{font-size:16px;font-weight:500;color:#000}

/* colored chips */
.green-chip{background:#b9f6ca!important}
.red-chip  {background:#ff8a80!important}

@media(max-width:700px){
  .details-flex-row{gap:16px}
}

.details-center {
  margin-left: auto;
  margin-right: auto;
}
</style>
