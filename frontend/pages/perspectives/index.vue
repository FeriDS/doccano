<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>{{ $t('perspectives.title') }}</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              class="text-capitalize mr-2"
              @click="$router.push(localePath('/perspectives/create'))"
            >
              {{ $t('perspectives.addPerspective') }}
            </v-btn>
            <v-btn
              text
              @click="goBack"
              aria-label="back"
            >
              <v-icon left>{{ mdiArrowLeft }}</v-icon>
              Return
            </v-btn>
          </v-card-title>

          <v-data-table
            :headers="headers"
            :items="perspectives"
            :loading="loading"
            :items-per-page="10"
            class="elevation-1"
            show-expand
            single-expand
          >
            <template #[`item.fields`]="{ item }">
              {{ item.fields ? item.fields.length : 0 }}
            </template>
            <template #[`item.created_at`]="{ item }">
              {{ new Date(item.created_at).toLocaleDateString() }}
            </template>
            <template #[`item.created_by_username`]="{ item }">
              {{ item.created_by_username }}
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
            <template #expanded-item="{ headers: tableHeaders, item }">
              <td :colspan="tableHeaders.length">
                <v-card flat>
                  <v-card-text>
                    <v-list>
                      <v-list-item
                        v-for="field in item.fields"
                        :key="field.id"
                      >
                        <v-list-item-content>
                          <v-list-item-title class="font-weight-bold">
                            {{ field.name }}
                          </v-list-item-title>
                          <v-list-item-subtitle>
                            {{ field.description }}
                          </v-list-item-subtitle>
                          <v-list-item-subtitle class="mt-2">
                            <v-chip
                              small
                              class="mr-2"
                              :color="getFieldTypeColor(field.field_type)"
                            >
                              {{ $t(`perspectives.fieldTypes.${field.field_type}`) }}
                            </v-chip>
                            <template 
                              v-if="field.field_type === 'choice' || 
                                    field.field_type === 'multiple'"
                            >
                              <v-chip
                                v-for="choice in field.choices"
                                :key="choice"
                                small
                                class="ml-2"
                              >
                                {{ choice }}
                              </v-chip>
                            </template>
                          </v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-card-text>
                </v-card>
              </td>
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
import { mdiPencil, mdiDelete, mdiArrowLeft } from '@mdi/js'
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
  mdiArrowLeft: any
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
      mdiArrowLeft,
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
          value: 'created_by_username'
        },
        { 
          text: this.$t('perspectives.createdAt').toString(),
          value: 'created_at'
        },
        { 
          text: this.$t('perspectives.actions').toString(),
          value: 'actions',
          sortable: false
        },
        {
          text: '',
          value: 'data-table-expand'
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
    // Check for message in URL query
    if (this.$route.query.message) {
      this.$store.dispatch('snackbar/show', {
        text: this.$route.query.message.toString(),
        color: this.$route.query.type || 'success',
        timeout: 5000,
        closable: true
      })
      // Remove the message from URL
      this.$router.replace({ query: {} })
    }
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
    },

    getFieldTypeColor(type: string): string {
      const colors: Record<string, string> = {
        text: 'primary',
        number: 'info',
        boolean: 'success',
        choice: 'warning',
        multiple: 'error'
      }
      return colors[type] || 'grey'
    },

    goBack() {
      this.$router.back()
    }
  }
})
</script> 