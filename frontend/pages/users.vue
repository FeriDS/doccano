<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h4 mb-4">Users</h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-alert
          v-model="showAlert"
          :type="alertType"
          :color="alertColor"
          class="mb-4"
          dismissible
        >
          {{ alertMessage }}
        </v-alert>
        <div class="d-flex justify-space-between align-center mb-4">
          <v-btn
            v-if="isAdmin"
            color="primary"
            @click="openCreateDialog"
            aria-label="Add User"
          >
            <v-icon left>{{ mdiAccountPlus }}</v-icon>
            Add User
          </v-btn>
          
          <v-btn icon @click="$router.back()" aria-label="Back">
            <v-icon>{{ mdiArrowLeft }}</v-icon>
            Return
          </v-btn>
        </div>

        <v-data-table
          :headers="tableHeaders"
          :items="users"
          :loading="loading"
          class="elevation-1"
          no-data-text="No data available"
          loading-text="Loading..."
        >
          <template #[`item.username`]="{ item }">
            {{ item.username || '-' }}
          </template>
          <template #[`item.email`]="{ item }">
            {{ item.email || '-' }}
          </template>
          <template #[`item.isStaff`]="{ item }">
            {{ item.isStaff ? 'Yes' : 'No' }}
          </template>
          <template #[`item.isSuperuser`]="{ item }">
            {{ item.isSuperuser ? 'Yes' : 'No' }}
          </template>
          <template #[`item.actions`]="{ item }">
            <v-menu v-if="isAdmin">
              <template #activator="{ on, attrs }">
                <v-btn icon v-bind="attrs" v-on="on" aria-label="Actions">
                  <v-icon>{{ mdiDotsVertical }}</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click="viewProfile(item)">
                  <v-list-item-title>View Profile</v-list-item-title>
                </v-list-item>
                <v-list-item @click="editUser(item)">
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

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Delete User</v-card-title>
        <v-card-text>
          Are you sure you want to delete this user? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="error" text @click="deleteUser">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { mdiAccount, mdiAccountPlus, mdiPencil, mdiDelete, mdiDotsVertical, mdiArrowLeft } from '@mdi/js'
import Vue from 'vue'
import { UserItem } from '~/domain/models/user/user'

export default Vue.extend({
  data() {
    return {
      loading: false,
      users: [] as UserItem[],
      deleteDialog: false,
      userToDelete: null as UserItem | null,
      mdiAccount,
      mdiAccountPlus,
      mdiPencil,
      mdiDelete,
      mdiDotsVertical,
      mdiArrowLeft,
      tableHeaders: [] as any[],
      isAdmin: false,
      showAlert: false,
      alertMessage: '',
      alertType: 'success',
      alertColor: 'success'
    }
  },

  async fetch() {
    this.loading = true
    try {
      this.users = await this.$repositories.user.list('')
      // Get current user profile to check if admin
      const profile = await this.$repositories.user.getProfile()
      this.isAdmin = profile.isSuperuser
    } catch (error) {
      this.$store.dispatch('snackbar/show', {
        text: 'Error loading users',
        color: 'error'
      })
    }
    this.loading = false
  },

  mounted() {
    this.tableHeaders = [
      { text: 'Username', value: 'username', sortable: true },
      { text: 'Email', value: 'email', sortable: true },
      { text: 'Staff', value: 'isStaff', sortable: true },
      { text: 'Superuser', value: 'isSuperuser', sortable: true },
      { text: 'Actions', value: 'actions', sortable: false }
    ];
  },

  methods: {
    openCreateDialog() {
      // TODO: Implement create user dialog
    },

    viewProfile(_user: UserItem) {
      // TODO: Implement view profile
    },

    editUser(_user: UserItem) {
      // TODO: Implement edit user
    },

    confirmDelete(user: UserItem) {
      this.userToDelete = user
      this.deleteDialog = true
    },

    async deleteUser() {
      if (!this.userToDelete) return

      try {
        await this.$repositories.user.deleteUser(this.userToDelete.id)
        this.users = this.users.filter(u => u.id !== this.userToDelete?.id)
        this.alertMessage = `User ${this.userToDelete.username} was successfully deleted`
        this.alertType = 'success'
        this.alertColor = 'success'
        this.showAlert = true
      } catch (error: any) {
        this.alertMessage = error.response?.data?.error || 'Error deleting user'
        this.alertType = 'error'
        this.alertColor = 'error'
        this.showAlert = true
      }
      this.deleteDialog = false
      this.userToDelete = null
    }
  }
})
</script> 