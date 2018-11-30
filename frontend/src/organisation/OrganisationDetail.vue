<template>
  <div class="card orgunit">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="users" />
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
          <mo-history :uuid="$route.params.uuid" type="ORG_UNIT"/>
        </div>
      </div>

      <organisation-detail-tabs
        :uuid="$route.params.uuid"
        :org-unit-info="orgUnit"
        :content="$store.getters['organisationUnit/GET_DETAILS']"
        @show="loadContent($event)"/>
    </div>
  </div>
</template>

<script>
/**
 * A organisation detail component.
 */

import { mapGetters } from 'vuex'
import { EventBus } from '@/EventBus'
import MoHistory from '@/components/MoHistory'
import OrganisationDetailTabs from './OrganisationDetailTabs'

export default {
  components: {
    MoHistory,
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
      orgUnit: 'organisationUnit/GET_ORG_UNIT'
    })
  },
  created () {
    this.$store.dispatch('organisationUnit/SET_ORG_UNIT', this.$route.params.uuid)
  },
  mounted () {
    EventBus.$on('organisation-unit-changed', () => {
      this.$store.dispatch('organisationUnit/SET_ORG_UNIT', this.$route.params.uuid)
      this.loadContent(this.latestEvent)
    })
  },
  methods: {
    loadContent (event) {
      this.latestEvent = event
      this.$store.dispatch('organisationUnit/SET_DETAIL', event)
    }
  },
  beforeRouteLeave (to, from, next) {
    this.$store.commit('organisationUnit/RESET_ORG_UNIT')
    next()
  }
}
</script>
