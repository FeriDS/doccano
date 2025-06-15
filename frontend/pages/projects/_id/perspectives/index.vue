<template>
  <v-container class="mt-12">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            {{ $t('perspectives.projectPerspective') }}
          </v-card-title>

          <v-card-text>
            <template v-if="loading">
              <v-skeleton-loader type="article" />
            </template>

            <template v-else-if="!projectPerspective">
              <v-alert
                type="info"
                class="mb-4"
              >
                {{ $t('perspectives.noPerspective') }}
              </v-alert>

              <v-select
                v-model="selectedPerspective"
                :items="availablePerspectives"
                item-text="name"
                item-value="id"
                :label="$t('perspectives.select')"
              />

              <v-btn
                color="primary"
                :disabled="!selectedPerspective"
                @click="assignPerspective"
              >
                {{ $t('perspectives.assign') }}
              </v-btn>
            </template>

            <template v-else>
              <v-alert v-if="!isAnnotationOpen" type="warning" class="mb-4">
                {{ $t('perspectives.annotationClosed') ||
                 'Annotation is closed for this project. You cannot edit your perspective.' }}
              </v-alert>
              <project-perspective-form
                :perspective="projectPerspective.perspective"
                :initial-values="userAnswer?.field_values || {}"
                :disabled="!isAnnotationOpen || isFinished"
                @submit="saveValues"
              />
            </template>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- ALERTA: mover para cá, logo após o card -->
    <v-row v-if="$route.query.redirected === 'true'">
      <v-col cols="12">
        <v-alert
          type="warning"
          class="mb-4"
          dismissible
        >
          <div class="d-flex align-center">
            <v-icon left>mdi-alert-circle</v-icon>
            <div>
              <strong>{{ $t('perspectives.perspectiveRequired') }}</strong><br>
              {{ $t('perspectives.fillBeforeAnnotate') }}
              {{ $t('perspectives.returnAfterFill') }}
            </div>
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Completion Status -->
    <v-row v-if="userAnswer">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            {{ $t('perspectives.status') }}
          </v-card-title>
          <v-card-text>
            <v-alert
              :type="userAnswer.is_complete ? 'success' : 'warning'"
            >
              {{ userAnswer.is_complete
                ? $t('perspectives.complete')
                : $t('perspectives.incomplete')
              }}
            </v-alert>

            <template v-if="!userAnswer.is_complete">
              <v-list>
                <v-list-item
                  v-for="field in missingFields"
                  :key="field"
                >
                  <v-list-item-icon>
                    <v-icon color="warning">mdi-alert</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ field }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </template>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import ProjectPerspectiveForm from '@/components/perspectives/ProjectPerspectiveForm.vue'
import { APIPerspectiveRepository } from '@/repositories/perspectives/apiPerspectiveRepository'
import { Perspective } from '@/domain/models/perspectives/perspective'
import { ProjectPerspective } from '@/domain/models/perspectives/projectPerspective'
import { UserPerspectiveAnswer } from '@/domain/models/perspectives/userPerspectiveAnswer'

interface Data {
  loading: boolean
  projectPerspective: ProjectPerspective | null
  userAnswer: UserPerspectiveAnswer | null
  availablePerspectives: Perspective[]
  selectedPerspective: number | null
  missingFields: string[]
  isAnnotationOpen: boolean
  example: any
}

export default Vue.extend({
  name: 'ProjectPerspectivesPage',

  components: {
    ProjectPerspectiveForm
  },

  data(): Data {
    return {
      loading: false,
      projectPerspective: null,
      userAnswer: null,
      availablePerspectives: [],
      selectedPerspective: null,
      missingFields: [],
      isAnnotationOpen: true,
      example: null
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },
    isFinished(): boolean {
      return this.example && this.example.is_finished
    }
  },

  async created() {
    await this.fetchData()
    await this.fetchExample()
  },

  methods: {
    async fetchData() {
      this.loading = true
      try {
        const repository = new APIPerspectiveRepository()
        
        // Get project perspective
        try {
          const projectPerspective = await repository.getProjectPerspective(this.projectId)
          this.projectPerspective = projectPerspective
          this.isAnnotationOpen = projectPerspective.is_annotation_open !== undefined ? 
          projectPerspective.is_annotation_open : true
        } catch (error) {
          if (error?.response?.status === 404) {
            // No project perspective assigned yet
            this.projectPerspective = null
            this.isAnnotationOpen = true
          } else {
            throw error
          }
        }

        // Get user's answer if perspective exists
        if (this.projectPerspective) {
          try {
            const userAnswer = await repository.getUserPerspectiveAnswer(this.projectId)
            this.userAnswer = userAnswer
          } catch (error) {
            // If no answer exists yet, that's fine
            console.log('No user answer found')
            this.userAnswer = null
          }
        }

        // Get available perspectives if no perspective is assigned
        if (!this.projectPerspective) {
          const perspectives = await repository.list()
          this.availablePerspectives = perspectives
        }
      } catch (error) {
        this.$snackbar.error(this.$t('generic.error').toString())
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async fetchExample() {
      // Busca o primeiro exemplo do projeto para verificar is_finished
      try {
        const result = await this.$services.example.list(this.projectId, { limit: '1' })
        this.example = result.items && result.items.length > 0 ? result.items[0] : null
      } catch (error) {
        this.example = null
      }
    },

    async assignPerspective() {
      if (!this.selectedPerspective) return

      try {
        const repository = new APIPerspectiveRepository()
        const perspective = await repository.findById(this.selectedPerspective)
        const projectPerspective = await repository.updateProjectPerspective(this.projectId, 
        perspective.id)
        this.projectPerspective = projectPerspective
        this.$snackbar.show({
          text: this.$t('perspectives.assigned').toString(),
          color: 'success',
          timeout: 5000
        })
        await this.fetchData()
      } catch (error) {
        let errorMessage = this.$t('generic.error').toString()
        if (error?.response?.data?.error) {
          errorMessage = error.response.data.error
        } else if (error?.response?.data?.message) {
          errorMessage = error.response.data.message
        }
        this.$snackbar.error(errorMessage)
        console.error('Error assigning perspective:', error)
      }
    },

    async saveValues(values: Record<string, any>) {
      try {
        const repository = new APIPerspectiveRepository()
        const userAnswer = await repository.updateUserPerspectiveAnswer(this.projectId, values)
        this.userAnswer = userAnswer || null
        await this.fetchData()
        // Lógica de redirecionamento conforme origem
        if (this.$route.query.from === 'sidebar' && this.$route.query.returnPath && this.userAnswer?.is_complete) {
          this.$snackbar.show({
            text: this.$t('perspectives.saved').toString(),
            color: 'success',
            timeout: 5000
          })
          setTimeout(() => {
            this.$router.push(this.$route.query.returnPath.toString())
          }, 5000)
        } else if (this.$route.query.redirected === 'true' && this.userAnswer?.is_complete) {
          this.$snackbar.show({
            text: this.$t('perspectives.saved').toString(),
            color: 'success',
            timeout: 5000
          })
          setTimeout(() => {
            this.$router.go(-1)
          }, 5000)
        } else {
          this.$snackbar.show({
            text: this.$t('perspectives.saved').toString(),
            color: 'success',
            timeout: 5000
          })
        }
      } catch (error) {
        let errorMessage = this.$t('generic.error').toString()
        if (error?.response?.data) {
          const errorData = error.response.data
          if (typeof errorData.error === 'string') {
            errorMessage = errorData.error
          } else if (typeof errorData.message === 'string') {
            errorMessage = errorData.message
          } else if (errorData.field_values && Array.isArray(errorData.field_values)) {
            errorMessage = errorData.field_values.join(', ')
          }
        }
        this.$snackbar.error(errorMessage)
        console.error('Error saving perspective values:', error)
      }
    }
  }
})
</script> 