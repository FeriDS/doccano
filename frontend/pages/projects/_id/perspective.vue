<template>
  <v-container>
    <v-row>
      <v-col>
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            <span>Gestão de Perspetiva</span>
          </v-card-title>
          <v-card-text>
            <perspective-form
              :project-id="projectId"
              :is-admin="isAdmin"
              @saved="onSaved"
              @cancel="onCancel"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import PerspectiveForm from '@/components/perspective/PerspectiveForm.vue'

export default {
  components: {
    PerspectiveForm
  },

  layout: 'project',

  middleware: ['auth', 'check-role'],

  data() {
    return {
      projectId: parseInt(this.$route.params.id)
    }
  },

  computed: {
    isAdmin() {
      return this.$store.getters['projects/isProjectAdmin']
    }
  },

  methods: {
    onSaved() {
      this.$router.push(`/projects/${this.projectId}/settings`)
    },

    onCancel() {
      this.$router.push(`/projects/${this.projectId}/settings`)
    }
  }
}
</script> 