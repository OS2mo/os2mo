<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>

      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-alt"/>
        {{employee.name}} <span class="cpr">({{employee.cpr_no | CPRNumber}})</span>
      </h4>

      <div class="row">
        <div class="col"></div>

        <div class="mr-3">
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
      getEmployee () {
        let vm = this
        vm.isLoading = true
        let uuid = this.$route.params.uuid
        Employee.get(uuid)
          .then(response => {
            vm.isLoading = false
            vm.employee = response
            vm.$store.commit('employee/change', response)
          })
      }
    }
  }
</script>

<style scoped>
  .cpr {
    color: #aaa
  }
</style>
