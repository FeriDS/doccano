<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h4 mb-4">Perfis</h1>
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
            color="primary"
            @click="openCreateDialog"
            aria-label="Adicionar Perfil"
          >
            <v-icon left>{{ mdiAccountPlus }}</v-icon>
            Adicionar Perfil
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
            <v-chip
              v-for="permission in item.permissions"
              :key="permission"
              class="mr-1"
              small
            >
              {{ permission }}
            </v-chip>
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
                  <v-list-item-title>Editar</v-list-item-title>
                </v-list-item>
                <v-list-item @click="confirmDelete(item)">
                  <v-list-item-title>Eliminar</v-list-item-title>
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
              :rules="[v => !!v || 'Nome é obrigatório']"
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
              label="Permissões"
              multiple
              chips
              :rules="[v => v.length > 0 || 'Pelo menos uma permissão é obrigatória']"
            ></v-select>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="closeDialog">
            Cancelar
          </v-btn>
          <v-btn color="primary" text @click="save" :disabled="!valid">
            Guardar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Eliminar Perfil</v-card-title>
        <v-card-text>
          Tem a certeza que pretende eliminar este perfil? Esta ação não pode ser revertida.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancelar
          </v-btn>
          <v-btn color="error" text @click="deleteProfile">
            Eliminar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { mdiAccountPlus, mdiDotsVertical } from '@mdi/js'
import Vue from 'vue'

interface Profile {
  id: number
  name: string
  description: string
  permissions: number[]
}

export default Vue.extend({
  data() {
    return {
      mdiAccountPlus,
      mdiDotsVertical,
      loading: false,
      dialog: false,
      deleteDialog: false,
      valid: false,
      showAlert: false,
      alertMessage: '',
      alertType: 'success',
      alertColor: 'success',
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
      availablePermissions: [
        'create_project',
        'edit_project',
        'delete_project',
        'view_project',
        'create_user',
        'edit_user',
        'delete_user',
        'view_user',
        'create_annotation',
        'edit_annotation',
        'delete_annotation',
        'view_annotation'
      ]
    }
  },

  computed: {
    formTitle(): string {
      return this.editedIndex === -1 ? 'Novo Perfil' : 'Editar Perfil'
    }
  },

  async fetch() {
    this.loading = true
    try {
      this.profiles = await this.$repositories.profile.list()
    } catch (error) {
      this.showAlert = true
      this.alertMessage = 'Erro ao carregar perfis'
      this.alertType = 'error'
      this.alertColor = 'error'
    }
    this.loading = false
  },

  methods: {
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
      })
    },

    async save() {
      if (!this.$refs.form.validate()) return

      try {
        if (this.editedIndex > -1) {
          await this.$repositories.profile.update(this.editedItem.id, this.editedItem)
          Object.assign(this.profiles[this.editedIndex], this.editedItem)
        } else {
          const newProfile = await this.$repositories.profile.create(this.editedItem)
          this.profiles.push(newProfile)
        }
        this.showAlert = true
        this.alertMessage = 'Perfil guardado com sucesso'
        this.alertType = 'success'
        this.alertColor = 'success'
      } catch (error) {
        this.showAlert = true
        this.alertMessage = 'Erro ao guardar perfil'
        this.alertType = 'error'
        this.alertColor = 'error'
      }
      this.closeDialog()
    },

    confirmDelete(item: Profile) {
      this.editedItem = Object.assign({}, item)
      this.deleteDialog = true
    },

    async deleteProfile() {
      try {
        await this.$repositories.profile.delete(this.editedItem.id)
        const index = this.profiles.indexOf(this.editedItem)
        this.profiles.splice(index, 1)
        this.showAlert = true
        this.alertMessage = 'Perfil eliminado com sucesso'
        this.alertType = 'success'
        this.alertColor = 'success'
      } catch (error) {
        this.showAlert = true
        this.alertMessage = 'Erro ao eliminar perfil'
        this.alertType = 'error'
        this.alertColor = 'error'
      }
      this.deleteDialog = false
    }
  }
})
</script> 