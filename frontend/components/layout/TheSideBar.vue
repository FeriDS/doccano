<template>
  <v-list dense>
    <v-btn color="ms-4 my-1 mb-2 primary text-capitalize" nuxt @click="toLabeling">
      <v-icon left>
        {{ mdiPlayCircleOutline }}
      </v-icon>
      {{ $t('home.startAnnotation') }}
    </v-btn>
    <v-btn color="secondary text-capitalize mb-2"
     nuxt :to="localePath(`/projects/${$route.params.id}/perspectives?
     from=sidebar&returnPath=${encodeURIComponent($route.path)}`)">
      <v-icon left>mdi-account</v-icon>
      {{$t('perspectives.projectPerspective')}}
    </v-btn>
    <v-list-item-group v-model="selected" mandatory>
      <v-list-item
        v-for="(item, i) in filteredItems"
        :key="i"
        @click="$router.push(localePath(`/projects/${$route.params.id}/${item.link}`))"
      >
        <v-list-item-action>
          <v-icon>
            {{ item.icon }}
          </v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>
            {{ item.text }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-menu
        v-if="isProjectAdmin"
        offset-y
        tile
        class="rounded-0"
      >
        <template #activator="{ on, attrs }">
          <v-list-item
            v-bind="attrs"
            v-on="on"
          >
            <v-list-item-action>
              <v-icon>
                {{ mdiClipboardListOutline }}
              </v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>
                Rules
              </v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>
                {{ mdiMenuDown }}
              </v-icon>
            </v-list-item-action>
          </v-list-item>
        </template>

        <v-list>
          <v-list-item
            v-if="isAdmin"
            :to="localePath(`/projects/${$route.params.id}/rules/create`)"
            exact
          >
            <v-list-item-icon>
              <v-icon>{{ mdiPlusCircleOutline }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>
              Create Rule
            </v-list-item-title>
          </v-list-item>
          <v-list-item @click="$router.push(localePath(`/projects/${$route.params.id}/rules`))">
            <v-list-item-action>
              <v-icon>
                mdi-check-all
              </v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>
                Vote Rules
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-list-item-group>
  </v-list>
</template>

<script>
import {
  mdiAccount,
  mdiBookOpenOutline,
  mdiChartBar,
  mdiCog,
  mdiCommentAccountOutline,
  mdiDatabase,
  mdiHome,
  mdiLabel,
  mdiPlayCircleOutline,
  mdiMenuDown,
  mdiPlus,
  mdiClipboardListOutline,
  mdiPlusCircleOutline
} from '@mdi/js'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'

export default {
  props: {
    isProjectAdmin: {
      type: Boolean,
      default: false,
      required: true
    },
    project: {
      type: Object,
      default: () => {},
      required: true
    }
  },

  data() {
    return {
      selected: 0,
      mdiPlayCircleOutline,
      mdiMenuDown,
      mdiPlus,
      mdiClipboardListOutline,
      isAdmin: false,
      mdiPlusCircleOutline
    }
  },

  computed: {
    filteredItems() {
      const items = [
        {
          icon: mdiHome,
          text: this.$t('projectHome.home'),
          link: '',
          isVisible: true
        },
        {
          icon: mdiDatabase,
          text: this.$t('dataset.dataset'),
          link: 'dataset',
          isVisible: true
        },
        {
          icon: mdiLabel,
          text: this.$t('labels.labels'),
          link: 'labels',
          isVisible:
            (this.isProjectAdmin || this.project.allowMemberToCreateLabelType) &&
            this.project.canDefineLabel
        },
        {
          icon: mdiLabel,
          text: 'Relations',
          link: 'links',
          isVisible:
            (this.isProjectAdmin || this.project.allowMemberToCreateLabelType) &&
            this.project.canDefineRelation
        },
        {
          icon: mdiAccount,
          text: this.$t('members.members'),
          link: 'members',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCommentAccountOutline,
          text: 'Comments',
          link: 'comments',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiBookOpenOutline,
          text: this.$t('guideline.guideline'),
          link: 'guideline',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiChartBar,
          text: this.$t('statistics.statistics'),
          link: 'metrics',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCog,
          text: this.$t('settings.title'),
          link: 'settings',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiChartBar,
          text: 'Annotation Statistics',
          link: 'annotation-statistics',
          isVisible: this.isProjectAdmin
        }
      ]
      return items.filter((item) => item.isVisible)
    }
  },

  methods: {
    toLabeling() {
      const query = this.$services.option.findOption(this.$route.params.id)
      const link = getLinkToAnnotationPage(this.$route.params.id, this.project.projectType)
      this.$router.push({
        path: this.localePath(link),
        query
      })
    }
  },

  async created() {
    try {
      const userRole = await this.$repositories.member.fetchMyRole(this.$route.params.id)
      this.isAdmin = userRole.isProjectAdmin
    } catch (err) {
      console.error('Erro ao buscar o papel do usuário:', err)
      this.isAdmin = false
    }
  }
}
</script>
