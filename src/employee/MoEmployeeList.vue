<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>
      <table class="table table-striped" v-show="!isLoading">
        <thead>
          <tr>
            <th scope="col">Navn</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="employee in employees" :key="employee.uuid">
            <td>
              <router-link class="nav-link" :to="{ name: 'EmployeeDetail', params: {'uuid': employee.uuid} }">
                {{employee.name}}
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script>
  import Employee from '@/api/Employee'
  import { EventBus } from '@/EventBus'
  import MoLoader from '@/components/atoms/MoLoader'

  export default {
    components: {
      MoLoader
    },
    data () {
      return {
        employees: [],
        isLoading: true
      }
    },
    mounted () {
      this.getEmployees()
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
        let org = this.$store.state.organisation
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
