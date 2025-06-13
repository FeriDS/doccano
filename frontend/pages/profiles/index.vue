<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h4 mb-4">Profiles</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <div class="d-flex justify-space-between align-center mb-4">
          <v-btn
            color="primary"
            @click="openCreateDialog"
            aria-label="Add Profile"
          >
            <v-icon left>{{ mdiAccountPlus }}</v-icon>
            Add Profile
          </v-btn>
          <v-btn
            icon
            @click="$router.go(-1)"
            aria-label="Back"
          >
            <v-icon>{{ mdiArrowLeft }}</v-icon>
          </v-btn>
        </div>

        <v-data-table
          :headers="tableHeaders"
          :items="profiles"
          :loading="loading"
          class="elevation-1"
          no-data-text="Não existem perfis disponíveis"
          loading-text="A carregar..."
        >
          <template #[`item.permissions`]="{ item }">
            <div v-if="item.permissions && item.permissions.length > 0">
              <v-chip
                v-for="permission in getPermissionNames(item.permissions)"
                :key="permission"
                class="mr-1 mb-1"
                small
                color="primary"
                outlined
              >
                {{ permission }}
              </v-chip>
            </div>
            <span v-else class="text-caption grey--text">No permissions</span>
          </template>

          <template #[`item.actions`]="{ item }">
            <v-menu>
              <template #activator="{ on, attrs }">
                <v-btn icon v-bind="attrs" v-on="on" aria-label="Ações">
                  <v-icon>{{ mdiDotsVertical }}</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click="editProfile(item)">
                  <v-list-item-title>Edit</v-list-item-title>
                </v-list-item>
                <v-list-item @click="confirmDelete(item)">
                  <v-list-item-title>Delete</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ formTitle }}</span>
        </v-card-title>

        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-text-field
              v-model="editedItem.name"
              label="Nome do Perfil"
              :rules="nameRules"
              required
            ></v-text-field>

            <v-textarea
              v-model="editedItem.description"
              label="Descrição"
              rows="3"
            ></v-textarea>

            <v-select
              v-model="editedItem.permissions"
              :items="availablePermissions"
              item-text="name"
              item-value="id"
              label="Permissões"
              multiple
              chips
              :rules="permissionRules"
              :error-messages="permissionError"
              :loading="loadingPermissions"
            >
              <template #no-data>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>
                      Loading permissions...
                    </v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-select>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="closeDialog">
            Cancel
          </v-btn>
          <v-btn color="primary" text @click="save" :disabled="!valid">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Delete Profile</v-card-title>
        <v-card-text>
          Are you certain you want to delete this profile? This action cannot be reverted.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="error" text @click="deleteProfile">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Alert Dialog -->
    <v-dialog v-model="showAlert" max-width="500px">
      <v-card>
        <v-card-title class="text-h5 error--text">
          {{ alertIcon === 'mdi-alert' ? 'Error' : 'Success' }}
        </v-card-title>
        <v-card-text>
          {{ alertMessage }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="showAlert = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { mdiAccountPlus, mdiDotsVertical, mdiArrowLeft } from '@mdi/js'
import Vue from 'vue'
import { AxiosInstance } from 'axios'

interface Profile {
  id: number
  name: string
  description: string
  permissions: number[]
}

interface FormRef extends Vue {
  validate(): boolean
}

interface Permission {
  id: number
  name: string
  codename: string
  content_type: number
}

export default Vue.extend({
  middleware: ['check-auth', 'auth'],
  data() {
    return {
      mdiAccountPlus,
      mdiDotsVertical,
      mdiArrowLeft,
      loading: false,
      loadingPermissions: false,
      dialog: false,
      deleteDialog: false,
      valid: false,
      showAlert: false,
      alertMessage: '',
      alertIcon: 'mdi-alert',
      profiles: [] as Profile[],
      editedIndex: -1,
      editedItem: {
        id: 0,
        name: '',
        description: '',
        permissions: [] as number[]
      },
      defaultItem: {
        id: 0,
        name: '',
        description: '',
        permissions: [] as number[]
      },
      tableHeaders: [
        { text: 'Nome', value: 'name' },
        { text: 'Descrição', value: 'description' },
        { text: 'Permissões', value: 'permissions' },
        { text: 'Ações', value: 'actions', sortable: false }
      ],
      availablePermissions: [] as Permission[],
      nameRules: [(v: string) => !!v || 'Nome é obrigatório'],
      permissionRules: [(v: number[]) => v.length > 0 || 'Pelo menos uma permissão é obrigatória'],
      permissionError: ''
    }
  },

  computed: {
    formTitle(): string {
      return this.editedIndex === -1 ? 'Novo Perfil' : 'Editar Perfil'
    }
  },

  async created() {
    await this.fetchPermissions()
    await this.fetchProfiles()
  },

  methods: {
    async fetchPermissions() {
      this.loadingPermissions = true
      try {
        const response = await (this.$axios as AxiosInstance).get('/v1/permissions/')
        this.availablePermissions = response.data
      } catch (error) {
        console.error('Error loading permissions:', error)
        this.showErrorMessage('Error loading permissions')
      } finally {
        this.loadingPermissions = false
      }
    },

    getPermissionNames(permissionIds: number[]): string[] {
      return permissionIds
        .map(id => this.availablePermissions.find(p => p.id === id)?.name)
        .filter((name): name is string => !!name)
    },

    async fetchProfiles() {
      this.loading = true
      try {
        this.profiles = await this.$repositories.profile.list()
      } catch (error) {
        console.error('Error loading profiles:', error)
        this.showErrorMessage('Error loading profiles')
      }
      this.loading = false
    },

    openCreateDialog() {
      this.editedItem = Object.assign({}, this.defaultItem)
      this.editedIndex = -1
      this.dialog = true
    },

    editProfile(item: Profile) {
      this.editedIndex = this.profiles.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    closeDialog() {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
        this.permissionError = ''
      })
    },

    async save() {
      const form = this.$refs.form as FormRef
      if (!form?.validate()) return

      if (this.editedItem.permissions.length === 0) {
        this.permissionError = 'At least one permission is required'
        return
      }

      try {
        if (this.editedIndex > -1) {
          await this.$repositories.profile.update(this.editedItem.id, this.editedItem)
          this.showSuccessMessage('Profile updated successfully')
        } else {
          await this.$repositories.profile.create(this.editedItem)
          this.showSuccessMessage('Profile created successfully')
          this.$router.push('/profiles')
        }
        this.closeDialog()
        await this.fetchProfiles()
      } catch (error: any) {
        console.error('Error saving profile:', error)
        let errorMessage = error.response?.data?.detail || 
                         error.response?.data?.name?.[0] || 
                         error.response?.data?.permissions?.[0] || 
                         'Error saving profile'
        errorMessage = errorMessage.replace(/user/i, 'User')
        this.showErrorMessage(errorMessage)
      }
    },

    confirmDelete(item: Profile) {
      this.editedItem = Object.assign({}, item)
      this.deleteDialog = true
    },

    async deleteProfile() {
      try {
        await this.$repositories.profile.delete(this.editedItem.id)
        await this.fetchProfiles()
        this.deleteDialog = false
        this.showSuccessMessage('Profile deleted successfully')
      } catch (error) {
        console.error('Error deleting profile:', error)
        this.showErrorMessage('Error deleting profile')
      }
    },

    showErrorMessage(message: string) {
      this.alertMessage = message.replace(/user/i, 'User')
      this.alertIcon = 'mdi-alert'
      this.showAlert = true
    },

    showSuccessMessage(message: string) {
      this.alertMessage = message
      this.alertIcon = 'mdi-check-circle'
      this.showAlert = true
    }
  }
})
</script>

<style scoped>
</style> 