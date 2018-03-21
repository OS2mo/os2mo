<template>
  <div class="card">
  <div class="card-body">
    <loading v-show="isLoading"/>
    <table class="table table-striped" v-show="!isLoading">
      <thead>
        <tr>
          <th scope="col">Navn</th>
        </tr>
      </thead>

      <tbody>
        <tr 
          v-for="employee in employees" 
          v-bind:key="employee.uuid"
        >
          <td>
            <router-link 
              class="nav-link" 
              :to="{ name: 'EmployeeDetail', params: {'uuid': employee.uuid} }"
            >
              {{employee.name}}
            </router-link></td>
        </tr>
      </tbody>
    </table>
  </div>
  </div>
</template>


<script>
  import Employee from '../api/Employee'
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
  import Loading from '../components/Loading'
  import '../filters/CPRNumber'

  export default {
    components: {
      Loading
    },
    data () {
      return {
        employees: [],
        isLoading: true
      }
    },
    created () {
      this.getEmployees()
    },
    mounted () {
      EventBus.$on('organisation-changed', () => {
        this.getEmployees()
      })
    },
    beforeDestroy () {
      EventBus.$off(['organisation-changed'])
    },
    methods: {
      getEmployees () {
        let vm = this
        vm.isLoading = true
        let org = Organisation.getSelectedOrganisation()
        if (org.uuid === undefined) return
        Employee.getAll(org.uuid)
          .then(response => {
            vm.employees = response
            vm.isLoading = false
          })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>