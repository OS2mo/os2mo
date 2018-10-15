<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="users" /> {{orgUnit.name}}
      </h4>

      <div class="row">
        <div class="col">
          <p class="card-text">Placering: {{orgUnit.location}}</p>
        </div>

        <div class="mr-3">
          <mo-history :uuid="$route.params.uuid" type="ORG_UNIT"/>
        </div>
      </div>

      <organisation-detail-tabs 
        :uuid="$route.params.uuid" 
        :content="$store.getters['organisationUnit/GET_DETAILS']" 
        @show="loadContent($event)"/>
    </div>
  </div>
</template>

<script>
  /**
   * A organisation detail component.
   */

  // import OrganisationUnit from '@/api/OrganisationUnit'
  import MoHistory from '@/components/MoHistory'
  import OrganisationDetailTabs from './OrganisationDetailTabs'

  export default {
    components: {
      MoHistory,
      OrganisationDetailTabs
    },
    created () {
      this.$store.dispatch('organisationUnit/SET_ORG_UNIT', this.$route.params.uuid)
    },
    computed: {
      orgUnit () {
        return this.$store.getters['organisationUnit/GET_ORG_UNIT']
      }
    },
    methods: {
      loadContent (event) {
        this.$store.dispatch('organisationUnit/SET_DETAIL', event)
      }
    },
    beforeRouteLeave (to, from, next) {
      this.$store.commit('organisationUnit/RESET_ORG_UNIT')
      next()
    }
  }
</script>
