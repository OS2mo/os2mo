<template>
  <div>
    <table class="table table-striped" v-show="!isLoading">
      <thead>
        <tr>
          <th scope="col">Adresse</th>
          <th scope="col">Lokationsnavn</th>
          <th scope="col">Primær adresse</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="location in locationsFuture" v-bind:key="location.uuid" style="color:#bbb">
          <td>{{location.location.vejnavn}}</td>
          <td>{{location.location.name}}</td>
          <td>{{location.primaer}}</td>
          <td>{{location['valid-from']}}</td>
          <td>{{location['valid-to']}}</td>
        </tr>

        <tr v-for="location in locations" v-bind:key="location.uuid">
          <td>{{location.location.vejnavn}}</td>
          <td>{{location.location.name}}</td>
          <td>{{location.primaer}}</td>
          <td>{{location['valid-from']}}</td>
          <td>{{location['valid-to']}}</td>
        </tr>
        
        <tr v-for="location in locationsPast" v-bind:key="location.uuid" style="color:#bbb">
          <td>{{location.location.vejnavn}}</td>
          <td>{{location.location.name}}</td>
          <td>{{location.primaer}}</td>
          <td>{{location['valid-from']}}</td>
          <td>{{location['valid-to']}}</td>
        </tr>
      </tbody>
    </table>

    <loading v-show="isLoading" />
  </div>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import Loading from '../components/Loading'

  export default {
    components: {
      Loading
    },
    props: {
      uuid: String
    },
    data () {
      return {
        locations: [],
        locationsPast: [],
        locationsFuture: [],
        isLoading: true
      }
    },
    created: function () {
      this.getLocations()
    },
    watch: {
      uuid (newVal, oldVal) {
        this.getLocations()
      }
    },
    methods: {
      getLocations: function () {
        var vm = this
        OrganisationUnit.getLocationDetails(this.uuid)
        .then(response => {
          vm.locations = response
          vm.isLoading = false
        })
        OrganisationUnit.getLocationDetails(this.uuid, 'past')
        .then(response => {
          vm.locationsPast = response
        })
        OrganisationUnit.getLocationDetails(this.uuid, 'future')
        .then(response => {
          vm.locationsFuture = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>