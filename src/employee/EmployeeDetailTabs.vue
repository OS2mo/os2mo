<template>
  <div>
    <loading v-show="isLoading"/>
    <b-tabs v-show="!isLoading">
      <b-tab title="Engagement" active v-if="tabs.engagement"> 
        <employee-detail-engagement :uuid="uuid"/>
      </b-tab>
      <b-tab title="Kontakt" v-if="tabs.engagement">
        <employee-detail-contact :uuid="uuid"/>
      </b-tab>
      <b-tab title="Rolle" v-if="tabs.role">
        <employee-detail-role :uuid="uuid"/>
      </b-tab>
      <b-tab title="IT" v-if="tabs.it">
        <employee-detail-it :uuid="uuid"/>
      </b-tab>
    </b-tabs>
  </div>
</template>


<script>
  import Employee from '../api/Employee'
  import EmployeeDetailEngagement from './EmployeeDetailEngagement'
  import EmployeeDetailContact from './EmployeeDetailContact'
  import EmployeeDetailRole from './EmployeeDetailRole'
  import EmployeeDetailIt from './EmployeeDetailIt'
  import Loading from '../components/Loading'

  export default {
    components: {
      EmployeeDetailEngagement,
      EmployeeDetailContact,
      EmployeeDetailRole,
      EmployeeDetailIt,
      Loading
    },
    props: {
      uuid: String
    },
    data () {
      return {
        tabs: {},
        isLoading: false
      }
    },
    created () {
      this.getTabs()
    },
    methods: {
      getTabs () {
        let vm = this
        vm.isLoading = true
        Employee.getDetailList(this.uuid)
        .then(response => {
          vm.isLoading = false
          vm.tabs = response
        })
      }
    }
  }
</script>
i