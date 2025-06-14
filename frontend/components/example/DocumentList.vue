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
    <template #[`item.isConfirmed`]="{ item: statusItem }">
      <v-chip :color="statusItem.isConfirmed ? 'success' : 'warning'" text small>
        {{ statusItem.isConfirmed ? 'Finished' : 'In progress' }}
      </v-chip>
    </template>
    <template #[`item.text`]="{ item: textItem }">
      <span class="d-flex d-sm-none">
        {{ textItem.text.length > 50 ? textItem.text.substring(0, 50) + '...' : textItem.text }}
      </span>
      <span class="d-none d-sm-flex">
        {{ textItem.text.length > 200 ? textItem.text.substring(0, 200) + '...' : textItem.text }}
      </span>
    </template>
    <template #[`item.meta`]="{ item: metaItem }">
      {{ JSON.stringify(metaItem.meta, null, 4) }}
    </template>
    <template #[`item.assignee`]="{ item: assigneeItem }">
      <v-combobox
        :value="toSelected(assigneeItem)"
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
        @change="onAssignOrUnassign(assigneeItem, $event)"
      >
        <template #selection="{ attrs, item, parent, selected }">
          <v-chip v-bind="attrs" :input-value="selected" small class="mt-1 mb-1">
            <span class="pr-1">{{ item.username }}</span>
            <v-icon small @click="parent.selectItem(item)"> $delete </v-icon>
          </v-chip>
        </template>
      </v-combobox>
    </template>
    <template #[`item.action`]="{ item: actionItem }">
      <v-btn class="me-1" small color="primary text-capitalize" @click="$emit('edit', actionItem)">
        Edit
      </v-btn>
      <v-btn small color="primary text-capitalize"
        :disabled="isAnnotationDisabled(actionItem)"
        @click="toLabeling(actionItem)">
        {{ $t('dataset.annotate') }}
      </v-btn>
    </template>
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
    <template v-if="mode === 'discrepancias' && isAdmin" #[`item.has_discrepancy`]="{ item }">
      <v-switch
        v-model="item.has_discrepancy"
        :label="$t('dataset.discrepancy') || 'Discrepancy'"
        dense
        hide-details
        @change="onDiscrepancyChange(item)"
        
      />
    </template>
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
    <template v-if="isAdmin" #[`item.annotation_end_date`]="{ item }">
      <v-text-field
        :value="formatDateForInput(item.annotation_end_date)"
        type="date"
        dense
        hide-details
        @change="val => $emit('update-date', item, 'annotation_end_date', val)"
        style="max-width: 140px"
      />
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { mdiMagnify } from '@mdi/js'
import type { PropType } from 'vue'
import Vue from 'vue'
import { DataOptions } from 'vuetify/types'
import { ExampleDTO } from '~/services/application/example/exampleData'
import { ExampleItem } from '~/domain/models/example/example'
import { MemberItem } from '~/domain/models/member/member'

export default Vue.extend({
  props: {
    isLoading: {
      type: Boolean,
      default: false,
      required: true
    },
    items: {
      type: Array as PropType<ExampleDTO[]>,
      default: () => [],
      required: true
    },
    value: {
      type: Array as PropType<ExampleDTO[]>,
      default: () => [],
      required: true
    },
    total: {
      type: Number,
      default: 0,
      required: true
    },
    members: {
      type: Array as PropType<MemberItem[]>,
      default: () => [],
      required: true
    },
    isAdmin: {
      type: Boolean,
      default: false
    },
    mode: {
      type: String,
      default: 'dataset'
    }
  },

  data() {
    return {
      search: this.$route.query.q,
      options: {} as DataOptions,
      mdiMagnify
    }
  },

  computed: {
    headers() {
      if (this.mode === 'discrepancias') {
        return [
          {
            text: this.$t('dataset.text'),
            value: 'text',
            sortable: false
          },
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
      } else {
        // dataset padrão
        const headers = [
          {
            text: 'Status',
            value: 'isConfirmed',
            sortable: false
          },
          {
            text: this.$t('dataset.text'),
            value: 'text',
            sortable: false
          },
          {
            text: this.$t('dataset.metadata'),
            value: 'meta',
            sortable: false
          },
          {
            text: 'Assignee',
            value: 'assignee',
            sortable: false
          },
          // Adicionar datas para admin
          ...(this.isAdmin ? [
            { text: 'Start Date', value: 'annotation_start_date', sortable: false },
            { text: 'End Date', value: 'annotation_end_date', sortable: false }
          ] : []),
          {
            text: this.$t('dataset.action'),
            value: 'action',
            sortable: false
          }
        ]
        return headers
      }
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
        query: {
          limit: this.options.itemsPerPage.toString(),
          offset: '0',
          q: this.search
        }
      })
      this.options.page = 1
    }
  },

  methods: {
    toLabeling(item: ExampleDTO) {
      const index = this.items.indexOf(item)
      const offset = (this.options.page - 1) * this.options.itemsPerPage
      const page = (offset + index + 1).toString()
      this.$emit('click:labeling', { page, q: this.search })
    },

    toSelected(item: ExampleDTO) {
      const assigneeIds = item.assignments.map((assignment) => assignment.assignee_id)
      return this.members.filter((member) => assigneeIds.includes(member.user))
    },

    onAssignOrUnassign(item: ExampleDTO, newAssignees: MemberItem[]) {
      const newAssigneeIds = newAssignees.map((assignee) => assignee.user)
      const oldAssigneeIds = item.assignments.map((assignment) => assignment.assignee_id)
      if (oldAssigneeIds.length > newAssigneeIds.length) {
        // unassign
        for (const assignment of item.assignments) {
          if (!newAssigneeIds.includes(assignment.assignee_id)) {
            this.$emit('unassign', assignment.id)
          }
        }
      } else {
        // assign
        for (const newAssigneeId of newAssigneeIds) {
          if (!oldAssigneeIds.includes(newAssigneeId)) {
            this.$emit('assign', item.id, newAssigneeId)
          }
        }
      }
    },

    onDiscrepancyChange(item: ExampleItem) {
      this.$emit('discrepancy-change', item)
    },

    isAnnotationDisabled(item: any) {
      const now = new Date()
      if (item.annotation_end_date) {
        const end = new Date(item.annotation_end_date)
        if (now > end) return true
      }
      if (item.is_finished) return true
      return false
    },

    formatDateForInput(date: any) {
      console.log('formatDateForInput:', date)
      if (!date) return ''
      if (/^\d{4}-\d{2}-\d{2}$/.test(date)) return date
      if (date.length >= 10) return date.slice(0, 10)
      return date
    }
  }
})
</script>
