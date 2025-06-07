<template>
  <v-card>
    <v-tabs v-model="tab">
      <v-tabs-slider color="primary" />
      <v-tab href="#tab-project" class="text-capitalize"> Project </v-tab>
      <v-tab href="#tab-auto-labeling" class="text-capitalize"> Auto Labeling </v-tab>
      <v-tab href="#tab-perspective" class="text-capitalize"> Perspetiva </v-tab>
    </v-tabs>
    <v-divider />

    <v-tabs-items v-model="tab">
      <v-tab-item value="tab-project">
        <form-update />
      </v-tab-item>
      <v-tab-item value="tab-auto-labeling">
        <config-list />
      </v-tab-item>
      <v-tab-item value="tab-perspective">
        <perspective-form
          :project-id="projectId"
          :is-admin="true"
          @saved="onPerspectiveSaved"
        />
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import FormUpdate from '@/components/project/FormUpdate.vue'
import ConfigList from '@/components/configAutoLabeling/ConfigList.vue'
import PerspectiveForm from '@/components/perspective/PerspectiveForm.vue'

export default Vue.extend({
  components: {
    ConfigList,
    FormUpdate,
    PerspectiveForm
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],

  validate({ params }) {
    return /^\d+$/.test(params.id)
  },

  data() {
    return {
      tab: null,
      projectId: parseInt(this.$route.params.id)
    }
  },

  methods: {
    onPerspectiveSaved() {
      this.$store.dispatch('snackbar/show', {
        text: 'Perspetiva atualizada com sucesso',
        color: 'success'
      })
    }
  }
})
</script>
