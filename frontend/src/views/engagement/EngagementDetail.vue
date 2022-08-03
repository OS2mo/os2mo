SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading" />

      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-alt" />
        {{ engagement.user_key }}
      </h4>

      <div class="row">
        <div class="col"></div>
      </div>
      <engagement-detail-tabs
        :uuid="route.params.uuid"
        :content="engagementDetails"
        @show="loadContent($event)"
      />
    </div>
  </div>
</template>

<script>
/**
 * A engagement detail component.
 */

import { EventBus, Events } from "@/EventBus"
import MoLoader from "@/components/atoms/MoLoader"
import { mapState, mapGetters } from "vuex"
import { Engagement } from "@/store/actions/engagement"
import { AtDate } from "@/store/actions/atDate"
import EngagementDetailTabs from "./EngagementDetailTabs"

export default {
  components: {
    EngagementDetailTabs,
    MoLoader,
  },

  data() {
    /**
     * The engagement, isLoading component value.
     * Used to detect changes and restore the value for columns.
     */
    return {
      isLoading: false,
      latestEvent: undefined,
      _atDate: undefined,
    }
  },

  computed: {
    ...mapState({
      route: "route",
    }),

    ...mapGetters({
      engagement: Engagement.getters.GET_ENGAGEMENT,
      engagementDetails: Engagement.getters.GET_DETAILS,
      atDate: AtDate.getters.GET,
    }),
  },

  watch: {
    atDate(newVal) {
      this._atDate = newVal
      if (this.latestEvent) {
        this.loadContent(this.latestEvent)
      }
    },
  },

  created() {
    this.$store.commit(Engagement.mutations.RESET_ENGAGEMENT)
    this.$store.dispatch(Engagement.actions.SET_ENGAGEMENT, this.$route.params.uuid)
  },

  mounted() {
    this._atDate = this.$store.getters[AtDate.getters.GET]
    EventBus.$on(Events.ENGAGEMENT_CHANGED, this.listener)
  },

  beforeDestroy() {
    EventBus.$off(Events.ENGAGEMENT_CHANGED, this.listener)
  },

  methods: {
    loadContent(event) {
      event.atDate = this._atDate
      this.latestEvent = event
      this.$store.dispatch(Engagement.actions.SET_DETAIL, event)
    },

    listener() {
      this.$store.dispatch(Engagement.actions.SET_ENGAGEMENT, this.$route.params.uuid)
      this.loadContent(this.latestEvent)
    },
  },
}
</script>
