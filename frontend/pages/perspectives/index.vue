<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <h2>{{ $t('perspectives.title') }}</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              class="text-capitalize"
              @click="$router.push(localePath('/perspectives/create'))"
            >
              {{ $t('perspectives.addPerspective') }}
            </v-btn>
          </v-card-title>

          <v-data-table
            :headers="headers"
            :items="perspectives"
            :loading="loading"
            :items-per-page="10"
            class="elevation-1"
          >
            <template #[`item.fields`]="{ item }">
              {{ item.fields ? item.fields.length : 0 }}
            </template>
            <template #[`item.createdAt`]="{ item }">
              {{ new Date(item.createdAt).toLocaleDateString() }}
            </template>
            <template #[`item.actions`]="{ item }">
              <v-icon
                small
                class="mr-2"
                @click="editPerspective(item)"
              >
                {{ mdiPencil }}
              </v-icon>
              <v-icon
                small
                @click="deletePerspective(item)"
              >
                {{ mdiDelete }}
              </v-icon>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title>{{ $t('perspectives.deleteConfirmation') }}</v-card-title>
        <v-card-text>{{ $t('perspectives.deleteConfirmationText') }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeDelete">{{ $t('perspectives.cancel') }}</v-btn>
          <v-btn color="error" text @click="deleteItemConfirm">
          {{ $t('perspectives.delete') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiPencil, mdiDelete } from '@mdi/js'
import { Perspective } from '@/domain/models/perspectives/perspective'

interface Data {
  deleteDialog: boolean
  perspectiveToDelete: Perspective | null
  headers: Array<{
    text: string
    value: string
    align?: string
    sortable?: boolean
  }>
  mdiPencil: any
  mdiDelete: any
}

export default Vue.extend({
  name: 'PerspectivesPage',

  layout: 'perspectives',

  middleware: ['check-auth', 'auth'],

  data(): Data {
    return {
      deleteDialog: false,
      perspectiveToDelete: null,
      mdiPencil,
      mdiDelete,
      headers: [
        {
          text: this.$t('perspectives.name').toString(),
          align: 'start',
          value: 'name'
        },
        { 
          text: this.$t('perspectives.description').toString(),
          value: 'description'
        },
        { 
          text: this.$t('perspectives.fields').toString(),
          value: 'fields'
        },
        { 
          text: this.$t('perspectives.createdBy').toString(),
          value: 'createdBy'
        },
        { 
          text: this.$t('perspectives.createdAt').toString(),
          value: 'createdAt'
        },
        { 
          text: this.$t('perspectives.actions').toString(),
          value: 'actions',
          sortable: false
        }
      ]
    }
  },

  computed: {
    perspectives() {
      return this.$store.getters['perspectives/allPerspectives']
    },
    loading() {
      return this.$store.getters['perspectives/isLoading']
    }
  },

  async created() {
    await this.fetchPerspectives()
  },

  methods: {
    async fetchPerspectives() {
      try {
        await this.$store.dispatch('perspectives/fetchPerspectives')
      } catch (error) {
        this.$store.dispatch('snackbar/show', {
          text: this.$t('perspectives.errorLoading').toString(),
          color: 'error'
        })
        console.error('Error fetching perspectives:', error)
      }
    },

    editPerspective(item: Perspective) {
      this.$router.push(this.localePath(`/perspectives/${item.id}/edit`))
    },

    deletePerspective(item: Perspective) {
      this.perspectiveToDelete = item
      this.deleteDialog = true
    },

    closeDelete() {
      this.deleteDialog = false
      this.perspectiveToDelete = null
    },

    async deleteItemConfirm() {
      if (!this.perspectiveToDelete) return

      try {
        await this.$store.dispatch('perspectives/deletePerspective', this.perspectiveToDelete.id)
        this.$store.dispatch('snackbar/show', {
          text: this.$t('perspectives.deleteSuccess').toString(),
          color: 'success'
        })
      } catch (error) {
        this.$store.dispatch('snackbar/show', {
          text: this.$t('perspectives.deleteError').toString(),
          color: 'error'
        })
        console.error('Error deleting perspective:', error)
      } finally {
        this.closeDelete()
      }
    }
  }
})
</script> 