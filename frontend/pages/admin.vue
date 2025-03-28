<template>
  <div class="admin-container">
    <div class="delete-user-box">
      <h2>Delete User</h2>
      <!-- v-autocomplete with custom item slot to avoid highlight -->
      <v-autocomplete
        v-model="username"
        :items="users"
        item-text="username"
        item-value="username"
        label="Select Username"
        outlined
        dense
      >
        <!-- Override default highlighting by defining a custom item slot -->
        <template #item="{ item }">
          {{ item.username }}
        </template>
      </v-autocomplete>

      <v-btn style="color: red; background-color: lightgray;" @click="deleteUser">
        Delete
      </v-btn>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapActions } from 'vuex'
import { APIUserRepository } from '~/repositories/user/apiUserRepository'

export default Vue.extend({
  name: 'Admin',
  data() {
    return {
      username: '',
      users: [] as any[], // or use the appropriate type
    }
  },
  mounted() {
    this.loadUsers();
  },
  methods: {
    ...mapActions('auth', ['logout']),

    async loadUsers() {
      try {
        const userRepository = new APIUserRepository();
        // Load all users
        this.users = await userRepository.list('');
      } catch (error: any) {
        console.error("Error loading users:", error);
      }
    },

    async deleteUser() {
      if(confirm("Tem a certeza que quer apagar o utilizador?")){ 
      if (!this.username) {
        alert("Please enter a username.");
        return;
      }

      try {
        const userRepository = new APIUserRepository();
        // Retrieve the user ID by username
        const userId = await userRepository.getIdByUsername(this.username);
        if (!userId) {
          alert("User not found.");
          return;
        }

        // Prevent self-deletion
        if (userId === this.$store.state.auth.id) {
          alert("You have been deleted!.");
          await userRepository.deleteUser(userId);
          await this.logout();
          await this.$router.push(this.localePath('/'));
          return;
        }

        // Delete the user
        await userRepository.deleteUser(userId);
        alert("User deleted successfully.");
        this.username = "";

        // Refresh user list after deletion
        await this.loadUsers();
      } catch (error: any) {
        console.error("Error deleting user:", error);
        alert(`Error: ${error?.message || "User not found"}`);
      }
    }
  }}
});
</script>

<style scoped>
.admin-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  flex-direction: column;
}

.delete-user-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
</style>