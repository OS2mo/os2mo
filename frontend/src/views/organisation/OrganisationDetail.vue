<template>
  <div class="card orgunit">
    <div class="card-body" v-if="orgUnit">
      <h4 class="card-title">
        <icon class="mr-1" name="users" />
        <span class="orgunit-name">{{orgUnit.name}}</span>
      </h4>

      <div class="row">
        <div class="col user-settings" v-if="orgUnit.user_settings.orgunit">
          <div class="card-text" v-if="orgUnit.user_settings.orgunit.show_location">
            {{$t('common.placement')}}:
            <span class="orgunit-location">{{orgUnit.location}}</span>
          </div>
          <div class="user-key card-text mb-3" v-if="orgUnit.user_settings.orgunit.show_user_key">
            {{$t('common.unit_number')}}:
            <span class="orgunit-user_key">{{orgUnit.user_key}}</span>
          </div>
        </div>

        <div class="mr-3" v-if="orgUnitIntegration">
          <mo-integration-button :uuid="route.params.uuid"/>
        </div>

        <div class="mr-3">
          <mo-history :uuid="route.params.uuid" type="ORG_UNIT"/>
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
      <mo-loader/>
    </div>
  </div>
</template>

<script>
/**
 * A organisation detail component.
 */

import { mapGetters, mapState } from 'vuex'
import { EventBus, Events } from '@/EventBus'
import MoHistory from '@/components/MoHistory'
import MoIntegrationButton from '@/components/MoIntegrationButton'
import MoLoader from '@/components/atoms/MoLoader'
import OrganisationDetailTabs from './OrganisationDetailTabs'
import { OrganisationUnit } from '@/store/actions/organisationUnit'

export default {
  components: {
    MoIntegrationButton,
    MoHistory,
    MoLoader,
    OrganisationDetailTabs
  },
  data () {
    return {
      latestEvent: undefined
    }
  },
  computed: {
    /**
     * Get organisation uuid.
     */
    ...mapGetters({
      orgUnit: OrganisationUnit.getters.GET_ORG_UNIT,
      orgUnitDetails: OrganisationUnit.getters.GET_DETAILS
    }),

    ...mapState({
      route: 'route'
    }),

    orgUnitIntegration () {
      return this.$store.getters['conf/GET_CONF_DB'].show_org_unit_button
    }

  },
  created () {
    this.$store.commit(OrganisationUnit.mutations.RESET_ORG_UNIT)
    this.$store.dispatch(OrganisationUnit.actions.SET_ORG_UNIT, this.route.params.uuid)
  },
  mounted () {
    EventBus.$on(Events.ORGANISATION_UNIT_CHANGED, this.listener)
  },
  beforeDestroy () {
    EventBus.$off(Events.ORGANISATION_UNIT_CHANGED, this.listener)
  },
  methods: {
    loadContent (event) {
      this.latestEvent = event
      this.$store.dispatch(OrganisationUnit.actions.SET_DETAIL, event)
    },
    listener () {
      this.$store.dispatch(OrganisationUnit.actions.SET_ORG_UNIT, this.route.params.uuid)
      this.loadContent(this.latestEvent)
    }
  }
}
</script>
<style scoped>
  .user-settings{
    color: #aaa;
  }
</style>

