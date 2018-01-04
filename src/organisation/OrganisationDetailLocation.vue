<template>
    <table class="table table-striped">
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
</template>

<script>
  import Organisation from '../api/Organisation'

  export default {
    components: {},
    data () {
      return {
        locations: [],
        locationssPast: [],
        locationsFuture: []
      }
    },
    created: function () {
      this.getLocations()
    },
    methods: {
      getLocations: function () {
        var vm = this
        Organisation.getLocationDetails(this.$route.params.uuid)
        .then(response => {
          vm.locations = response
        })
        Organisation.getLocationDetails(this.$route.params.uuid, 'past')
        .then(response =>{
          vm.locationsPast = response
        })
        Organisation.getLocationDetails(this.$route.params.uuid, 'future')
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