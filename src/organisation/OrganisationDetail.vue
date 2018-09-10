<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="users" /> {{orgUnit.name}}
      </h4>

      <div class="row">
        <div class="col">
          <p class="card-text">Placering: {{orgUnit.path}}</p>
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
      MoHistory,
      OrganisationDetailTabs
    },

    data () {
      return {
        orgUnit: {}
      }
    },

    mounted () {
      this.updateDetails()
    },

    methods: {
      updateDetails () {
        var vm = this
        OrganisationUnit.get(this.$route.params.uuid)
          .then(response => {
            vm.orgUnit = response
            vm.$store.commit('organisationUnit/change', response)
          })
      }
    }
  }
</script>
