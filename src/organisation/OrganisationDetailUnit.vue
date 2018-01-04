<template>
  <div>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Enhedsnavn</th>
          <th scope="col">Enhedstype</th>
          <th scope="col">Overenhed</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="unit in detailsFuture" v-bind:key="unit.uuid" style="color:#bbb">
          <td>{{unit.name}}</td>
          <td>{{unit.type.name}}</td>
          <td><span v-if="unit['parent-object']">{{unit['parent-object'].name}}</span></td>
          <td>{{unit['valid-from']}}</td>
          <td>{{unit['valid-to']}}</td>
        </tr>

        <tr v-for="unit in details" v-bind:key="unit.uuid">
          <td>{{unit.name}}</td>
          <td>{{unit.type.name}}</td>
          <td><span v-if="unit['parent-object']">{{unit['parent-object'].name}}</span></td>
          <td>{{unit['valid-from']}}</td>
          <td>{{unit['valid-to']}}</td>
        </tr>

        <tr v-for="unit in detailsPast" v-bind:key="unit.uuid" style="color:#bbb">
          <td>{{unit.name}}</td>
          <td>{{unit.type.name}}</td>
          <td><span v-if="unit['parent-object']">{{unit['parent-object'].name}}</span></td>
          <td>{{unit['valid-from']}}</td>
          <td>{{unit['valid-to']}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
  import Organisation from '../api/Organisation'

  export default {
    components: {},
    data () {
      return {
        details: [],
        detailsPast: [],
        detailsFuture: []
      }
    },
    created: function () {
      this.getDetails()
    },
    methods: {
      getDetails: function () {
        var vm = this
        Organisation.getUnitDetails(this.$route.params.uuid)
        .then(function (response) {
          vm.details = response
        })
        Organisation.getUnitDetails(this.$route.params.uuid, 'past')
        .then(function (response) {
          vm.detailsPast = response
        })
        Organisation.getUnitDetails(this.$route.params.uuid, 'future')
        .then(function (response) {
          vm.detailsFuture = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>