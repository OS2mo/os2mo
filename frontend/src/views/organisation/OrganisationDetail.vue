SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <div class="card orgunit">
      <div class="card-body" v-if="orgUnit">
        <h4 class="card-title">
          <icon class="mr-1" name="users" />
          <span class="orgunit-name">{{ orgUnit.name }}</span>
        </h4>

        <div class="row">
          <div class="col user-settings" v-if="orgUnit.user_settings.orgunit">
            <div class="card-text" v-if="orgUnit.user_settings.orgunit.show_location">
              {{ $t("common.placement") }}:
              <span class="orgunit-location">{{ orgUnit.location }}</span>
            </div>
            <div
              class="user-key card-text mb-3"
              v-if="orgUnit.user_settings.orgunit.show_user_key"
            >
              {{ $t("common.unit_number") }}:
              <span class="orgunit-user_key">{{ orgUnit.user_key }}</span>
            </div>
          </div>

          <div class="mr-3" v-if="orgUnitIntegration">
            <mo-integration-button :uuid="route.params.uuid" />
          </div>
        </div>

        <organisation-detail-tabs
          :uuid="route.params.uuid"
          :org-unit-info="orgUnit"
          :content="orgUnitDetails"
          @show="loadContent($event)"
        />
      </div>

      <div class="card-body" v-show="!orgUnit">
        <mo-loader />
      </div>
    </div>

    <mo-log />
  </div>
</template>

<script>
/**
 * A organisation detail component.
 */

import { mapGetters, mapState } from "vuex"
import { EventBus, Events } from "@/EventBus"
import MoIntegrationButton from "@/components/MoIntegrationButton"
import MoLog from "@/components/MoLog/MoLog"
import MoLoader from "@/components/atoms/MoLoader"
import OrganisationDetailTabs from "./OrganisationDetailTabs"
import { OrganisationUnit } from "@/store/actions/organisationUnit"
import { AtDate } from "@/store/actions/atDate"

export default {
  components: {
    MoIntegrationButton,
    MoLog,
    MoLoader,
    OrganisationDetailTabs,
  },

  data() {
    return {
      latestEvent: undefined,
      _atDate: undefined,
    }
  },

  computed: {
    /**
     * Get organisation uuid.
     */
    ...mapGetters({
      orgUnit: OrganisationUnit.getters.GET_ORG_UNIT,
      orgUnitDetails: OrganisationUnit.getters.GET_DETAILS,
      atDate: AtDate.getters.GET,
    }),

    ...mapState({
      route: "route",
    }),

    orgUnitIntegration() {
      return this.$store.getters["conf/GET_CONF_DB"].show_org_unit_button
    },
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
    this.$store.commit(OrganisationUnit.mutations.RESET_ORG_UNIT)
    this.$store.dispatch(OrganisationUnit.actions.SET_ORG_UNIT, {
      uuid: this.route.params.uuid,
      atDate: this.atDate,
    })
  },

  mounted() {
    this._atDate = this.$store.getters[AtDate.getters.GET]
    EventBus.$on(Events.ORGANISATION_UNIT_CHANGED, this.listener)
  },

  beforeDestroy() {
    EventBus.$off(Events.ORGANISATION_UNIT_CHANGED, this.listener)
  },

  methods: {
    loadContent(event) {
      event.atDate = this._atDate
      this.latestEvent = event
      this.$store.dispatch(OrganisationUnit.actions.SET_DETAIL, event)
    },

    listener() {
      this.$store.dispatch(OrganisationUnit.actions.SET_ORG_UNIT, {
        uuid: this.route.params.uuid,
        atDate: this.atDate,
      })
      this.loadContent(this.latestEvent)
    },
  },
}
</script>
<style scoped>
.user-settings {
  color: #aaa;
}
</style>
