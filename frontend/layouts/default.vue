<template>
  <v-app>
    <v-snackbar
      v-model="$store.state.snackbar.show"
      :color="$store.state.snackbar.color"
      :timeout="$store.state.snackbar.timeout"
      top
    >
      {{ $store.state.snackbar.text }}
      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="$store.dispatch('snackbar/hide')">
          {{ $t('generic.close') }}
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      v-model="showTechIssue"
      :timeout="0"
      top
      color="error"
    >
      {{ techIssueMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="showTechIssue = false">
          Ok
        </v-btn>
      </template>
    </v-snackbar>
    <the-header />
    <nuxt />
    <the-footer />
  </v-app>
</template>

<script>
import TheFooter from "@/components/layout/TheFooter";
import TheHeader from "@/components/layout/TheHeader";

export default {
  components: {
    TheFooter,
    TheHeader,
  },
  data() {
    return {
      showTechIssue: false,
    };
  },
  computed: {
    techIssueMessage() {
      if (this.showTechIssue) {
        return 'Database connection is down. Please try again later.';
      }
      return '';
    },
  },
  mounted() {
    const params = new URLSearchParams(window.location.search);
    if (params.get("error") === "techissue") {
      this.showTechIssue = true;
    }
  },
};
</script>

<style scoped></style>
