<template>
  <div class="card">
    <div class="card-body d-flex flex-column">
      <mo-loader v-show="isLoading"/>
      <div id="employee-list-wrapper">
        <table class="table table-striped" v-show="!isLoading">
          <thead>
            <tr>
              <th scope="col">{{$t('table_headers.person')}}</th>
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

<style scoped>
.card-body {
  min-height: 5vh;
  max-height: 75vh;
}

#employee-list-wrapper {
  height: 100%;
  overflow-x: hidden;
  overflow-y: scroll
}
</style>
