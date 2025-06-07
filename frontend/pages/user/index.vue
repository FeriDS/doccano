<template>
  <v-container class="mt-16">
    <v-row>
      <v-col>
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <span class="text-h5">Users</span>
              <v-btn
                v-if="isAdmin"
                color="primary"
                class="ml-4"
                @click="openCreateDialog"
              >
                <v-icon left>{{ mdiAccountPlus }}</v-icon>
                Add User
              </v-btn>
            </div>
            <v-btn
              text
              @click="$router.back()"
              aria-label="Return"
            >
              <v-icon left>{{ mdiArrowLeft }}</v-icon>
              Return
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-data-table
              :headers="tableHeaders"
              :items="users"
              :loading="loading"
              class="mt-4"
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
                <v-menu>
                  <template #activator="{ on, attrs }">
                    <v-btn icon v-bind="attrs" aria-label="Actions" v-on="on" >
                      <v-icon>{{ mdiDotsVertical }}</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item 
                      v-if="isAdmin || (currentUserId && currentUserId === item.id)" 
                      @click="editUser(item)"
                    >
                      <v-list-item-icon>
                        <v-icon>{{ mdiPencil }}</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Edit</v-list-item-title>
                    </v-list-item>
                    <v-list-item 
                      v-if="isAdmin && currentUserId !== item.id" 
                      @click="confirmDelete(item)"
                      class="error--text"
                    >
                      <v-list-item-icon>
                        <v-icon color="error">{{ mdiDelete }}</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Delete</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Edit User Dialog -->
    <v-dialog v-model="editDialog" max-width="500px">
      <edit-user-form
        v-if="editDialog"
        :user="userToEdit"
        :is-admin="isSuperuser && currentUserId !== userToEdit?.id"
        @saved="onUserUpdated"
        @cancel="closeEditDialog"
      />
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title>Delete User</v-card-title>
        <v-card-text>Are you sure you want to delete this user? 
        This action cannot be undone.</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="deleteDialog = false">No</v-btn>
          <v-btn color="error" @click="deleteUser">Yes</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Alert -->
    <v-snackbar
      v-model="showAlert"
      :color="alertColor"
      timeout="5000"
    >
      {{ alertMessage }}
    </v-snackbar>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import {
  mdiAccount,
  mdiAccountPlus,
  mdiPencil,
  mdiDelete,
  mdiDotsVertical,
  mdiArrowLeft
} from '@mdi/js'
import { UserItem } from '@/domain/models/user/user'
import EditUserForm from '@/components/user/EditUserForm.vue'

export default Vue.extend({
  components: {
    EditUserForm
  },

  data() {
    return {
      loading: false,
      users: [] as UserItem[],
      deleteDialog: false,
      editDialog: false,
      userToDelete: null as UserItem | null,
      userToEdit: null as UserItem | null,
      currentUserId: null as number | null,
      mdiAccount,
      mdiAccountPlus,
      mdiPencil,
      mdiDelete,
      mdiDotsVertical,
      mdiArrowLeft,
      tableHeaders: [
        { text: 'Username', value: 'username', sortable: true },
        { text: 'First Name', value: 'first_name', sortable: true },
        { text: 'Last Name', value: 'last_name', sortable: true },
        { text: 'Email', value: 'email', sortable: true },
        { text: 'Staff', value: 'isStaff', sortable: true },
        { text: 'Superuser', value: 'isSuperuser', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
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
      // Get current user profile first to ensure ID is set
      const profile = await this.$repositories.user.getProfile()
      this.isAdmin = profile.isSuperuser
      this.currentUserId = profile.id
      // Set user ID in store first
      this.$store.commit('auth/setUserId', profile.id)
      this.$store.commit('auth/setIsSuperuser', profile.isSuperuser)

      // Then fetch users list
      this.users = await this.$repositories.user.list('')
      
      console.log('Debug fetch:', {
        profile,
        users: this.users,
        currentUserId: this.currentUserId,
        isAdmin: this.isAdmin
      })
    } catch (error) {
      this.$store.dispatch('snackbar/show', {
        text: 'Erro ao carregar utilizadores',
        color: 'error'
      })
    }
    this.loading = false
  },

  computed: {
    isSuperuser(): boolean {
      return this.$store.getters['auth/isSuperuser']
    },
    isCurrentUser(): boolean {
      return this.currentUserId === this.userToEdit?.id
    }
  },

  methods: {
    openCreateDialog() {
      // TODO: Implement create user dialog
    },

    viewProfile(_user: UserItem) {
      // TODO: Implement view profile
    },

    editUser(user: UserItem) {
      console.log('Debug editUser:', {
        user,
        currentUserId: this.currentUserId,
        isAdmin: this.isAdmin,
        storeState: this.$store.state.auth
      })
      this.userToEdit = user
      this.editDialog = true
    },

    closeEditDialog() {
      this.editDialog = false
      this.userToEdit = null
    },

    async onUserUpdated() {
      await this.$fetch()
      this.closeEditDialog()
      this.showAlert = true
      this.alertMessage = 'Utilizador atualizado com sucesso'
      this.alertType = 'success'
      this.alertColor = 'success'
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
        this.alertMessage = 'Utilizador apagado com sucesso'
        this.alertType = 'success'
        this.alertColor = 'success'
        this.showAlert = true
      } catch (error: any) {
        this.alertMessage = error.response?.data?.error || 'Erro ao apagar utilizador'
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