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
          <td>{{d.name}}</td>
          <td>{{d.user_name}}</td>
          <td>{{d.valid_from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.valid_to | moment('DD-MM-YYYY')}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../api/Employee'

  export default {
    data () {
      return {
        details: []
      }
    },
    created () {
      this.getDetails()
    },
    methods: {
      getDetails () {
        var vm = this
        Employee.getItDetails(this.$route.params.uuid)
        .then(response => {
          vm.details = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>