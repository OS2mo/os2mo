<template>
  <div>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Enhed</th>
          <th scope="col">Stillingsbetegnelse</th>
          <th scope="col">Engagementstype</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="d in details" v-bind:key="d.uuid">
          <td><router-link :to="{ name: 'OrganisationDetail', params: {'uuid': d.org_unit.uuid} }">{{d.org_unit.name}}</router-link></td>
          <td>{{d.job_function | getProperty('name')}}</td>
          <td>
              {{d.type | getProperty('name')}}
          </td>
          <td>{{d.valid_from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.valid_to | moment('DD-MM-YYYY')}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../api/Employee'
  import '../filters/GetProperty'

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
        Employee.getEngagementDetails(this.$route.params.uuid)
        .then(response => {
          console.log(response)
          vm.details = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>