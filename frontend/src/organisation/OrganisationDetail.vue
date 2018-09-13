<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="users" /> {{orgUnitInfo.name}}
      </h4>
      <div class="row" v-if="orgUnitInfo.user_settings">
	<p class="card-text" v-if="orgUnitInfo.user_settings.orgunit.show_location">Placering: {{orgUnitInfo.location}}</p>
	<p class="card-text" v-if="orgUnitInfo.user_settings.orgunit.show_bvn">Enhedsnr.: {{orgUnitInfo.user_key}}</p>
        </div>

        <div class="mr-3">
          <mo-history :uuid="$route.params.uuid" type="ORG_UNIT"/>
        </div>
      </div>

      <organisation-detail-tabs :uuid="$route.params.uuid"/>
    </div>
  </div>
</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoHistory from '@/components/MoHistory'
  import OrganisationDetailTabs from './OrganisationDetailTabs'

  export default {
    components: {
      MoHistory: MoHistory,
      OrganisationDetailTabs
    },

    data () {
      return {
        orgUnitInfo: {}
      }
    },

    created () {
      this.updateDetails()
    },

    methods: {
      updateDetails () {
        OrganisationUnit.get(this.$route.params.uuid)
          .then(response => {
            this.orgUnitInfo = response
            this.$store.commit('organisationUnit/change', response)
          })
      }
    }
  }
</script>
