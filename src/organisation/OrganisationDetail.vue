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

      <ul class="nav nav-tabs">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'OrganisationDetailUnit' }">
            Enhed
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'OrganisationDetailLocation' }">
            Lokation
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'OrganisationDetailContact' }">
            Kontaktkanal
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'OrganisationDetailEngagement' }">
            Engagementer
          </router-link>
        </li>
      </ul>

      <router-view/>
    </div>
  </div>
</template>


<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import TheHistory from '../components/TheHistory'

  export default {
    components: {
      TheHistory
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
.router-link-active {
  color: #495057;
  background-color: #fff;
  border-color: #ddd #ddd #fff;
}

</style>