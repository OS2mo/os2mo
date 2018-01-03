<template>
  <div class="card">
  <div class="card-body">
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Navn</th>
          <th scope="col">CPR. Nr.</th>
          <th scope="col">Brugernavn</th>
        </tr>
      </thead>

      <tbody>
        <tr 
          v-for="employee in employees" 
          v-bind:key="employee.uuid"
        >
          <td>
          <router-link class="nav-link" :to="{ name: 'EmployeeDetail', params: {'uuid': employee.uuid} }">
              {{employee.name}}
            </router-link></td>
          <td>{{employee['user-key']}}</td>
          <td>{{employee['nick-name']}}</td>
        </tr>
      </tbody>
    </table>
  </div>
  </div>
</template>


<script>
  import Employee from '../api/Employee'

  export default {
    components: {},
    data () {
      return {
        employees: []
      }
    },
    created: function () {
      this.getEmployees()
    },
    methods: {
      getEmployees: function () {
        var vm = this
        Employee.getAll()
        .then(response => {
          vm.employees = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>