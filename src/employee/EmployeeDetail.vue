<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>
      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-o"/>
        {{employee.name}} <span class="cpr">({{employee.cpr_no | CPRNumber}})</span>
      </h4>
      <div class="row">
        <div class="mr-auto">
        </div>
        <div>
          <mo-history :uuid="$route.params.uuid" type="EMPLOYEE"/>
        </div>
      </div>
      <employee-detail-tabs :uuid="$route.params.uuid"/>
    </div>
  </div>
</template>

<script>
  import Employee from '@/api/Employee'
  import '@/filters/CPRNumber'
  import EmployeeDetailTabs from './EmployeeDetailTabs'
  import MoHistory from '@/components/MoHistory'
  import MoLoader from '@/components/atoms/MoLoader'

  export default {
    components: {
      EmployeeDetailTabs,
      MoHistory,
      MoLoader
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
      getEmployee (uuid) {
        var vm = this
        vm.isLoading = true
        Employee.get(uuid)
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
