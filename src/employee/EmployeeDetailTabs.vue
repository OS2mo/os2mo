<template>
  <div>
    <b-tabs>
      <b-tab title="Engagement" active v-if="tabs.engagement"> 
        <employee-detail-engagement :uuid="uuid"/>
      </b-tab>
      <b-tab title="Kontakt" v-if="tabs.engagement">
        <employee-detail-contact :uuid="uuid"/>
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
  import EmployeeDetailIt from './EmployeeDetailIt'
  export default {
    components: {
      EmployeeDetailEngagement,
      EmployeeDetailContact,
      EmployeeDetailIt
    },
    props: {
      uuid: String
    },
    data () {
      return {
        tabs: {}
      }
    },
    created () {
      this.getTabs()
    },
    methods: {
      getTabs () {
        Employee.getDetailList(this.uuid)
        .then(respone => {
          this.tabs = respone
        })
      }
    }
  }
</script>
i