<template>
  <v-data-table
    :value="value"
    :headers="headers"
    :items="items"
    :options.sync="options"
    :server-items-length="total"
    :search="search"
    :loading="isLoading"
    :loading-text="$t('generic.loading')"
    :no-data-text="$t('vuetify.noDataAvailable')"
    :footer-props="{
      showFirstLastPage: true,
      'items-per-page-options': [10, 50, 100],
      'items-per-page-text': $t('vuetify.itemsPerPageText'),
      'page-text': $t('dataset.pageText')
    }"
    item-key="id"
    show-select
    @input="$emit('input', $event)"
  >
    <!-- TOP BAR -------------------------------------------------------- -->
    <template #top>
      <v-text-field
        v-model="search"
        :prepend-inner-icon="mdiMagnify"
        :label="$t('generic.search') + ' (e.g. label:positive)'"
        single-line
        hide-details
        filled
      />
    </template>

    <!-- STATUS --------------------------------------------------------- -->
    <template #[`item.isConfirmed`]="{ item }">
      <v-chip :color="item.isConfirmed ? 'success' : 'warning'" text small>
        {{ item.isConfirmed ? 'Finished' : 'In progress' }}
      </v-chip>
    </template>

    <!-- TEXT ----------------------------------------------------------- -->
    <template #[`item.text`]="{ item }">
      <span class="d-flex d-sm-none">
        {{ item.text.length > 50 ? item.text.substring(0, 50) + '...' : item.text }}
      </span>
      <span class="d-none d-sm-flex">
        {{ item.text.length > 200 ? item.text.substring(0, 200) + '...' : item.text }}
      </span>
    </template>

    <!-- META ----------------------------------------------------------- -->
    <template #[`item.meta`]="{ item }">
      {{ JSON.stringify(item.meta, null, 4) }}
    </template>

    <!-- ASSIGNEE ------------------------------------------------------- -->
    <template #[`item.assignee`]="{ item }">
      <v-combobox
        :value="toSelected(item)"
        :items="members"
        item-text="username"
        no-data-text="No one"
        multiple
        chips
        dense
        flat
        hide-selected
        hide-details
        small-chips
        solo
        style="width: 200px"
        @change="onAssignOrUnassign(item, $event)"
      >
        <template #selection="{ attrs, item: m, parent, selected }">
          <v-chip v-bind="attrs" :input-value="selected" small class="mt-1 mb-1">
            <span class="pr-1">{{ m.username }}</span>
            <v-icon small @click="parent.selectItem(m)">$delete</v-icon>
          </v-chip>
        </template>
      </v-combobox>
    </template>

    <!-- ACTION --------------------------------------------------------- -->
    <template #[`item.action`]="{ item }">
      <v-btn class="me-1" small color="primary text-capitalize" @click="$emit('edit', item)">
        Edit
      </v-btn>
      <v-btn
        small
        color="primary text-capitalize"
        :disabled="isAnnotationDisabled(item)"
        @click="toLabeling(item)"
      >
        {{ $t('dataset.annotate') }}
      </v-btn>
    </template>

    <!-- LABEL DISTRIBUTION -------------------------------------------- -->
    <template v-if="mode === 'discrepancias'" #[`item.label_distribution`]="{ item }">
      <div>
        <v-chip
          v-for="(percent, label) in item.label_distribution"
          :key="label"
          small
          class="ma-1"
        >
          {{ label }}: {{ percent }}%
        </v-chip>
      </div>
    </template>

    <!-- DISCREPÂNCIA --------------------------------------------------- -->
    <template v-if="mode === 'discrepancias' && isAdmin" #[`item.has_discrepancy`]="{ item }">
      <template v-if="displayDiscrepancyAsText">
        {{ item.has_discrepancy ? 'true' : 'false' }}
      </template>
      <template v-else>
        <v-switch
          v-model="item.has_discrepancy"
          :label="$t('dataset.discrepancy') || 'Discrepancy'"
          dense
          hide-details
          @change="onDiscrepancyChange(item)"
        />
      </template>
    </template>

    <!-- START DATE ----------------------------------------------------- -->
    <template v-if="isAdmin" #[`item.annotation_start_date`]="{ item }">
      <v-text-field
        :value="formatDateForInput(item.annotation_start_date)"
        type="date"
        dense
        hide-details
        style="max-width: 140px"
        @change="val => $emit('update-date', item, 'annotation_start_date', val)"
      />
    </template>

    <!-- END DATE ------------------------------------------------------- -->
    <template v-if="isAdmin" #[`item.annotation_end_date`]="{ item }">
      <v-text-field
        :value="formatDateForInput(item.annotation_end_date)"
        type="date"
        dense
        hide-details
        style="max-width: 140px"
        @change="val => $emit('update-date', item, 'annotation_end_date', val)"
      />
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { mdiMagnify } from '@mdi/js'
import Vue from 'vue'
import type { PropType } from 'vue'
import { DataOptions } from 'vuetify/types'
import { ExampleDTO } from '~/services/application/example/exampleData'
import { ExampleItem } from '~/domain/models/example/example'
import { MemberItem } from '~/domain/models/member/member'

export default Vue.extend({
  props: {
    isLoading: { type: Boolean, default: false },
    items: { type: Array as PropType<ExampleDTO[]>, default: () => [] },
    value: { type: Array as PropType<ExampleDTO[]>, default: () => [] },
    total: { type: Number, default: 0 },
    members: { type: Array as PropType<MemberItem[]>, default: () => [] },
    isAdmin: { type: Boolean, default: false },
    mode: { type: String, default: 'dataset' },
    displayDiscrepancyAsText: { type: Boolean, default: false }
  },

  data() {
    return {
      search: this.$route.query.q,
      options: {} as DataOptions,
      mdiMagnify
    }
  },

  computed: {
    headers(): any[] {
      if (this.mode === 'discrepancias') {
        return [
          { text: this.$t('dataset.text'), value: 'text', sortable: false },
          {
            text: this.$t('dataset.labelDistribution') || 'Label Distribution',
            value: 'label_distribution',
            sortable: false
          },
          {
            text: this.$t('dataset.discrepancy') || 'Discrepancy',
            value: 'has_discrepancy',
            sortable: false
          }
        ]
      }
      return [
        { text: 'Status', value: 'isConfirmed', sortable: false },
        { text: this.$t('dataset.text'), value: 'text', sortable: false },
        { text: this.$t('dataset.metadata'), value: 'meta', sortable: false },
        { text: 'Assignee', value: 'assignee', sortable: false },
        ...(this.isAdmin
          ? [
              { text: 'Start Date', value: 'annotation_start_date', sortable: false },
              { text: 'End Date', value: 'annotation_end_date', sortable: false }
            ]
          : []),
        { text: this.$t('dataset.action'), value: 'action', sortable: false }
      ]
    }
  },

  watch: {
    options: {
      handler() {
        this.$emit('update:query', {
          query: {
            limit: this.options.itemsPerPage.toString(),
            offset: ((this.options.page - 1) * this.options.itemsPerPage).toString(),
            q: this.search
          }
        })
      },
      deep: true
    },
    search() {
      this.$emit('update:query', {
        query: { limit: this.options.itemsPerPage.toString(), offset: '0', q: this.search }
      })
      this.options.page = 1
    }
  },

  methods: {
    /* ---------- navegação ----------- */
    toLabeling(item: ExampleDTO) {
      const idx = this.items.indexOf(item)
      const offset = (this.options.page - 1) * this.options.itemsPerPage
      this.$emit('click:labeling', { page: (offset + idx + 1).toString(), q: this.search })
    },

    /* ---------- assignee helpers ----- */
    toSelected(item: ExampleDTO) {
      const ids = item.assignments.map(a => a.assignee_id)
      return this.members.filter(m => ids.includes(m.user))
    },

    onAssignOrUnassign(item: ExampleDTO, newAssignees: MemberItem[]) {
      const newIds = newAssignees.map(a => a.user)
      const oldIds = item.assignments.map(a => a.assignee_id)

      // unassign
      oldIds
        .filter(id => !newIds.includes(id))
        .forEach(id =>
          this.$emit('unassign', item.assignments.find(a => a.assignee_id === id)?.id)
        )

      // assign
      newIds
        .filter(id => !oldIds.includes(id))
        .forEach(id => this.$emit('assign', item.id, id))
    },

    /* ---------- discrepância -------- */
    onDiscrepancyChange(item: ExampleItem) {
      this.$emit('discrepancy-change', item)
    },

    /* ---------- utilidades ---------- */
    isAnnotationDisabled(item: any) {
      const now = new Date()
      if (item.annotation_end_date && now > new Date(item.annotation_end_date)) return true
      return !!item.is_finished
    },

    formatDateForInput(date: any) {
      if (!date) return ''
      if (/^\d{4}-\d{2}-\d{2}$/.test(date)) return date
      return date.slice(0, 10)
    }
  }
})
</script>
