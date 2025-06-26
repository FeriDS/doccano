<!-- eslint-disable -->
<template>
  <v-list dense>
    <!-- ── QUICK ACTIONS ─────────────────────────────── -->
    <v-btn
      color="ms-4 my-1 mb-2 primary text-capitalize"
      nuxt
      @click="toLabeling"
    >
      <v-icon left>{{ mdiPlayCircleOutline }}</v-icon>
      {{ $t('home.startAnnotation') }}
    </v-btn>

    <v-btn
      color="secondary text-capitalize mb-2"
      nuxt
      :to="localePath(
        `/projects/${$route.params.id}/perspectives?from=sidebar&returnPath=${encodeURIComponent(
          $route.path
        )}`)"
    >
      <v-icon left>mdi-account</v-icon>
      {{ $t('perspectives.projectPerspective') }}
    </v-btn>

    <!-- ── MAIN NAVIGATION LIST ──────────────────────── -->
    <v-list-item-group v-model="selected" mandatory>
      <v-list-item
        v-for="(item, i) in filteredItems"
        :key="i"
        @click="$router.push(localePath(`/projects/${$route.params.id}/${item.link}`))"
      >
        <v-list-item-action>
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>{{ item.text }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <!-- ── REPORT (before Rules) ───────────────────── -->
      <template v-if="isProjectAdmin">
        <v-menu offset-y>
          <template #activator="{ on, attrs }">
            <v-list-item v-bind="attrs" v-on="on">
              <v-list-item-action>
                <v-icon >{{ mdiFileDocumentOutline }}</v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title>
                  <!-- added report symbol -->
                  
                Annotations Reports
                </v-list-item-title>
              </v-list-item-content>
              <v-list-item-action>
                <v-icon>{{ mdiMenuDown }}</v-icon>
              </v-list-item-action>
            </v-list-item>
          </template>
          <v-list>
            <v-list-item
              @click="
                $router.push(
                  localePath(`/projects/${projectId}/annotation-statistics/report?historic=true`)
                )
              "
            >
              <v-list-item-action>
                <span style="display:inline-flex;align-items:center;">
                  <svg width="24" height="24" viewBox="0 0 24 24" style="vertical-align:middle;">
                    <circle cx="12" cy="12" r="8" fill="none" stroke="#555" stroke-width="2"/>
                    <rect x="10" y="2" width="4" height="3" rx="1" fill="#555"/>
                    <rect x="10" y="19" width="4" height="3" rx="1" fill="#555"/>
                    <line x1="12" y1="12" x2="12" y2="8" stroke="#555" stroke-width="2" stroke-linecap="round"/>
                    <line x1="12" y1="12" x2="15" y2="12" stroke="#555" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </span>
              </v-list-item-action>
              <v-list-item-title>With historic</v-list-item-title>
            </v-list-item>
            <v-list-item
              @click="
                $router.push(
                  localePath(`/projects/${projectId}/annotation-statistics/report`)
                )
              "
            >
              <v-list-item-action>
                <span style="display:inline-flex;align-items:center;">
                  <svg width="24" height="24" viewBox="0 0 24 24" style="vertical-align:middle;">
                    <rect x="4" y="6" width="16" height="12" rx="2" fill="none" stroke="#555" stroke-width="2"/>
                    <line x1="4" y1="10" x2="20" y2="10" stroke="#555" stroke-width="2"/>
                    <line x1="4" y1="14" x2="20" y2="14" stroke="#555" stroke-width="2"/>
                    <line x1="8" y1="6" x2="8" y2="18" stroke="#555" stroke-width="2"/>
                    <line x1="16" y1="6" x2="16" y2="18" stroke="#555" stroke-width="2"/>
                  </svg>
                </span>
              </v-list-item-action>
              <v-list-item-title>Without historic</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>

      <!-- ── RULES (last entry) ───────────────────────── -->
      <v-menu offset-y tile class="rounded-0">
        <template #activator="{ on, attrs }">
          <v-list-item v-bind="attrs" v-on="on">
            <v-list-item-action>
              <v-icon>{{ mdiClipboardListOutline }}</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Rules</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>{{ mdiMenuDown }}</v-icon>
            </v-list-item-action>
          </v-list-item>
        </template>

        <v-list>
          <v-list-item
            v-if="isSuperUser"
            :to="localePath(`/projects/${projectId}/rules/create`)"
            exact
          >
            <v-list-item-icon>
              <v-icon>{{ mdiPlusCircleOutline }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Create Rule</v-list-item-title>
          </v-list-item>

          <v-list-item
            @click="$router.push(localePath(`/projects/${$route.params.id}/rules`))"
          >
            <v-list-item-action>
              <v-icon>mdi-check-all</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Vote Rules</v-list-item-title>
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
  mdiPlusCircleOutline,
  mdiFileDocumentOutline,
  mdiClockOutline
} from '@mdi/js'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'

export default {
  props: {
    isProjectAdmin: { type: Boolean, required: true, default: false },
    project: { type: Object, required: true, default: () => ({}) }
  },

  data() {
    return {
      selected: 0,
      mdiPlayCircleOutline,
      mdiMenuDown,
      mdiPlus,
      mdiClipboardListOutline,
      mdiPlusCircleOutline,
      mdiChartBar,
      mdiFileDocumentOutline,
      mdiClockOutline
    }
  },

  computed: {
    projectId() {
      return this.project?.id || this.$route.params.id
    },
    filteredItems() {
      const items = [
        { icon: mdiHome, text: this.$t('projectHome.home'), link: '', isVisible: true },
        { icon: mdiDatabase, text: this.$t('dataset.dataset'), link: 'dataset', isVisible: true },
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
      return items.filter((i) => i.isVisible)
    },
    isSuperUser() {
      return this.$store.getters['auth/isSuperuser']
    }
  },

  methods: {
    toLabeling() {
      const query = this.$services.option.findOption(this.$route.params.id)
      const link = getLinkToAnnotationPage(
        this.$route.params.id,
        this.project.projectType
      )
      this.$router.push({ path: this.localePath(link), query })
    }
  }
}
</script>
