<template>
  <div class="card orgunit">
    <div class="card-body" v-if="orgUnit">
      <h4 class="card-title">
        <icon class="mr-1" name="users" />
        <span class="orgunit-name">{{orgUnit.name}}</span>
      </h4>

      <div class="row">
          <div class="col" v-if="orgUnit.user_settings.orgunit">
            <p class="card-text" v-if="orgUnit.user_settings.orgunit.show_location">
              {{$t('common.placement')}}:
              <span class="orgunit-location">{{orgUnit.location}}</span>
            </p>
            <p class="card-text" v-if="orgUnit.user_settings.orgunit.show_user_key">
              {{$t('common.unit_number')}}:
              <span class="orgunit-user_key">{{orgUnit.user_key}}</span>
            </p>
        </div>

        <div class="mr-3">
          <mo-history :uuid="route.params.uuid" type="ORG_UNIT"/>
        </div>
      </div>

      <organisation-detail-tabs
        :uuid="route.params.uuid"
        :org-unit-info="orgUnit"
        :content="orgUnitDetails"
        @show="loadContent($event)"/>
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
import { EventBus } from '@/EventBus'
import MoHistory from '@/components/MoHistory'
import MoLoader from '@/components/atoms/MoLoader'
import OrganisationDetailTabs from './OrganisationDetailTabs'
import { OrganisationUnit } from '@/store/actions/organisationUnit'

export default {
  components: {
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
    })
  },
  created () {
    this.$store.dispatch(OrganisationUnit.actions.SET_ORG_UNIT, this.route.params.uuid)
  },
  mounted () {
    EventBus.$on('organisation-unit-changed', () => {
      this.loadContent(this.latestEvent)
    })
  },
  methods: {
    loadContent (event) {
      this.latestEvent = event

      this.$store.dispatch(OrganisationUnit.actions.SET_ORG_UNIT, this.route.params.uuid)
      this.$store.dispatch(OrganisationUnit.actions.SET_DETAIL, event)
    }
  },
  beforeRouteLeave (to, from, next) {
    this.$store.commit(OrganisationUnit.mutations.RESET_ORG_UNIT)
    next()
  }
}
</script>
