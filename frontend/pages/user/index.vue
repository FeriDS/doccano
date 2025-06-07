<template>
  <v-container>
    <v-row>
      <v-col>
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            <span>Utilizadores</span>
            <v-btn
              v-if="isAdmin"
              color="primary"
              @click="openCreateDialog"
            >
              <v-icon left>{{ mdiAccountPlus }}</v-icon>
              Adicionar Utilizador
            </v-btn>
          </v-card-title>
          <v-data-table
            :headers="tableHeaders"
            :items="users"
            :loading="loading"
          >
            <template #[`item.username`]="{ item }">
              {{ item.username || '-' }}
            </template>
            <template #[`item.email`]="{ item }">
              {{ item.email || '-' }}
            </template>
            <template #[`item.isStaff`]="{ item }">
              {{ item.isStaff ? 'Sim' : 'Não' }}
            </template>
            <template #[`item.isSuperuser`]="{ item }">
              {{ item.isSuperuser ? 'Sim' : 'Não' }}
            </template>
            <template #[`item.actions`]="{ item }">
              <v-menu>
                <template #activator="{ on, attrs }">
                  <v-btn icon v-bind="attrs" aria-label="Ações" v-on="on" >
                    <v-icon>{{ mdiDotsVertical }}</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="viewProfile(item)">
                    <v-list-item-title>Ver Perfil</v-list-item-title>
                  </v-list-item>
                  <v-list-item 
                    v-if="isAdmin || (currentUserId && currentUserId === item.id)" 
                    @click="editUser(item)"
                  >
                    <v-list-item-title>Editar</v-list-item-title>
                  </v-list-item>
                  <v-list-item 
                    v-if="isAdmin && currentUserId !== item.id" 
                    @click="confirmDelete(item)"
                  >
                    <v-list-item-title>Apagar</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table>
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
        <v-card-title>Apagar Utilizador</v-card-title>
        <v-card-text>Tem certeza que deseja apagar este utilizador?
         Esta ação não pode ser desfeita.</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="deleteDialog = false">Não</v-btn>
          <v-btn color="error" @click="deleteUser">Sim</v-btn>
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
        { text: 'Nome de Utilizador', value: 'username', sortable: true },
        { text: 'Nome', value: 'first_name', sortable: true },
        { text: 'Sobrenome', value: 'last_name', sortable: true },
        { text: 'Email', value: 'email', sortable: true },
        { text: 'Staff', value: 'isStaff', sortable: true },
        { text: 'Superutilizador', value: 'isSuperuser', sortable: true },
        { text: 'Ações', value: 'actions', sortable: false }
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