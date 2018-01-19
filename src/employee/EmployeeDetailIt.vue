<template>
  <div>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">System</th>
          <th scope="col">Brugernavn</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="d in details" v-bind:key="d.uuid">
          <td>{{d['it-system'].name}}</td>
          <td>{{d['user-name']}}</td>
          <td>{{d['valid-from']}}</td>
          <td>{{d['valid-to']}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../api/Employee'

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
        Employee.getItDetails(this.$route.params.uuid)
        .then(function (response) {
          vm.details = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>