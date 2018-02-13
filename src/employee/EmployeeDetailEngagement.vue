<template>
  <div>
    <loading v-show="isLoading"/>
    <table class="table table-striped" v-show="!isLoading">
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
              {{d.engagement_type | getProperty('name')}}
          </td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../api/Employee'
  import '../filters/GetProperty'
  import Loading from '../components/Loading'

  export default {
    components: {
      Loading
    },
    props: {
      uuid: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        details: [],
        detailsPast: [],
        detailsFuture: [],
        isLoading: false
      }
    },
    created () {
      this.getDetails()
    },
    methods: {
      getDetails () {
        var vm = this
        vm.isLoading = true
        Employee.getEngagementDetails(this.uuid)
        .then(response => {
          vm.isLoading = false
          vm.details = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>