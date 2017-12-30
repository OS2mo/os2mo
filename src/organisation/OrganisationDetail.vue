<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="share-alt" /> Organisationer
      </h4>

      <div class="row">
        <div class="mr-auto">
          <p class="card-text">
            Enhed: {{orgUnit.name}} Enhedsnr.: {{orgUnit['user-key']}}
          </p>
        </div>
        <div class="">
          <button class="btn btn-outline-primary">
            <icon name="edit" />
          </button>
          <button class="btn btn-outline-primary" v-b-modal.theHistory>
            <icon name="book" />
          </button>
          <b-modal id="theHistory" size="lg" hide-footer title="Historik">
            <the-history/>
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
      </ul>

      <router-view/>
    </div>
  </div>
</template>


<script>
  import Organisation from '../api/Organisation'
  import OrganisationDetailContact from './OrganisationDetailContact'
  import TheHistory from '../components/TheHistory'

  export default {
    components: {
      OrganisationDetailContact,
      TheHistory
    },
    data () {
      return {
        orgUnit: {}
      }
    },
    created: function () {
      this.updateDetails()
    },
    methods: {
      updateDetails: function () {
        var vm = this
        Organisation.getOrganisationUnit('456362c4-0ee4-4e5e-a72c-751239745e62', this.$route.params.uuid)
        .then(function (response) {
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