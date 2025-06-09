<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-alert
          v-if="$route.query.redirected === 'true'"
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
              <project-perspective-form
                :perspective="projectPerspective.perspective"
                :initial-values="userAnswer?.field_values || {}"
                @submit="saveValues"
              />
            </template>
          </v-card-text>
        </v-card>
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
      missingFields: []
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    }
  },

  async created() {
    await this.fetchData()
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
        } catch (error) {
          if (error?.response?.status === 404) {
            // No project perspective assigned yet
            this.projectPerspective = null
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

    async assignPerspective() {
      if (!this.selectedPerspective) return

      try {
        const repository = new APIPerspectiveRepository()
        const perspective = await repository.findById(this.selectedPerspective)
        const projectPerspective = await repository.updateProjectPerspective(this.projectId, 
        perspective.id)
        this.projectPerspective = projectPerspective
        this.$snackbar.success(this.$t('perspectives.assigned').toString())
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
        
        // Check if user was redirected here
        const wasRedirected = this.$route.query.redirected
        const fromSidebar = this.$route.query.from === 'sidebar'
        const returnPath = this.$route.query.returnPath
        
        console.log('=== SAVE COMPLETED ===')
        console.log('wasRedirected:', wasRedirected, 'type:', typeof wasRedirected)
        console.log('fromSidebar:', fromSidebar, 'returnPath:', returnPath)
        console.log('Current route:', this.$route.path)
        console.log('Current route query:', this.$route.query)
        
        // Refresh data to get updated completion status
        console.log('Chamando fetchData...')
        await this.fetchData()
        console.log('fetchData completado')
        
        console.log('isComplete after fetchData:', this.userAnswer?.is_complete)
        
        // Determine if we should redirect back
        let shouldRedirectBack = false
        
        if ((wasRedirected === 'true') && this.userAnswer?.is_complete) {
          // Case 1: Redirected from annotation page
          shouldRedirectBack = true
        } else if (fromSidebar && returnPath && this.userAnswer?.is_complete) {
          // Case 2: Came from sidebar with a return path
          shouldRedirectBack = true
        }
        
        console.log('shouldRedirectBack:', shouldRedirectBack)
        
        if (shouldRedirectBack) {
          console.log('🔄 CASO: REDIRECIONAMENTO de volta')
          this.$snackbar.success(this.$t('perspectives.savedRedirecting').toString())
          setTimeout(() => {
            try {
              console.log('Executando redirecionamento...')
              
              // Check if we came from sidebar with a specific return path
              const returnPath = this.$route.query.returnPath
              if (returnPath) {
                console.log('Redirecting to specific path:', returnPath)
                this.$router.push(returnPath.toString())
                return
              }
              
              // Otherwise use browser history
              console.log('History length:', window.history.length)
              if (window.history.length > 1) {
                this.$router.go(-1)
              } else {
                console.log('Fallback: indo para projeto principal')
                this.$router.push(`/projects/${this.projectId}`)
              }
            } catch (error) {
              console.error('Erro ao redirecionar:', error)
              this.$router.push(`/projects/${this.projectId}`)
            }
          }, 1500)
        } else {
          console.log('✅ CASO: NAVEGAÇÃO DIRETA - NÃO redirecionando')
          this.$snackbar.success(this.$t('perspectives.saved').toString())
          console.log('Permanecendo na página atual - FIM')
        }
      } catch (error) {
        let errorMessage = this.$t('generic.error').toString()
        
        // Extract error message from response
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