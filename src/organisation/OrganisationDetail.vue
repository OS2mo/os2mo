<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="users" /> {{orgUnit.name}}
      </h4>

      <div class="row">
        <div class="mr-auto">
          <p class="card-text">
            Enhedsnr.: {{orgUnit.user_key}}
          </p>
        </div>
        <div>
          <button class="btn btn-outline-primary">
            <icon name="edit" />
          </button>
          <!-- <button class="btn btn-outline-primary" v-b-modal.viewUnit>
            <icon name="eye" />
          </button> -->
          <button class="btn btn-outline-primary" v-b-modal.theHistory>
            <icon name="book" />
          </button>
          <!-- <b-modal id="viewUnit" size="lg" hide-footer title="Vis enhed">
            <organisation-detail-view/>
          </b-modal> -->
          <b-modal id="theHistory" size="lg" hide-footer title="Historik">
            <the-history :unit-uuid="$route.params.uuid"/>
          </b-modal>
        </div>
      </div>

      <organisation-detail-tabs :uuid="$route.params.uuid"/>
    </div>
  </div>
</template>


<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import TheHistory from '../components/TheHistory'
  import OrganisationDetailTabs from './OrganisationDetailTabs'

  export default {
    components: {
      TheHistory,
      OrganisationDetailTabs
    },
    data () {
      return {
        orgUnit: {}
      }
    },
    created () {
      this.updateDetails()
    },
    methods: {
      updateDetails () {
        var vm = this
        OrganisationUnit.get(this.$route.params.uuid)
        .then(response => {
          vm.orgUnit = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>