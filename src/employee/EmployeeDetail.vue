<template>
  <div class="card">
    <div class="card-body">
      <loading v-show="isLoading"/>
      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-o"/>
        {{employee.name}} <span class="cpr">({{employee.cpr_no | CPRNumber}})</span>
      </h4>
      <div class="row">
        <div class="mr-auto">
        </div>
        <div>
          <button class="btn btn-outline-primary" v-b-modal.employeeEdit>
            <icon name="edit" />
          </button>
          <button class="btn btn-outline-primary">
            <icon name="book" />
          </button>
        </div>
      </div>
      <!-- Modal Component -->
      <employee-edit :uuid="$route.params.uuid"/>

      <employee-detail-tabs :uuid="$route.params.uuid"/>
    </div>
  </div>
</template>

<script>
  import Employee from '../api/Employee'
  import '../filters/CPRNumber'
  import EmployeeEdit from './EmployeeEdit'
  import EmployeeDetailTabs from './EmployeeDetailTabs'
  import Loading from '../components/Loading'

  export default {
    components: {
      EmployeeEdit,
      EmployeeDetailTabs,
      Loading
    },
    data () {
      return {
        employee: Object,
        isLoading: false
      }
    },
    created () {
      this.getEmployee(this.$route.params.uuid)
    },
    methods: {
      getEmployee: function (uuid) {
        var vm = this
        vm.isLoading = true
        Employee.getEmployee(uuid)
        .then(response => {
          vm.isLoading = false
          vm.employee = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.cpr {
  color: #aaa
}

</style>
