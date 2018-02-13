<template>
  <div>
    <loading v-show="isLoading"/>
    <b-tabs v-show="!isLoading">
      <b-tab title="Engagement" active v-if="tabs.engagement"> 
        <employee-detail-engagement :uuid="uuid"/>
      </b-tab>
      <b-tab title="Adresser" v-if="tabs.address">
        <employee-detail-contact :uuid="uuid"/>
      </b-tab>
      <b-tab title="Rolle" v-if="tabs.role">
        <employee-detail-role :uuid="uuid"/>
      </b-tab>
      <b-tab title="IT" v-if="tabs.it">
        <employee-detail-it :uuid="uuid"/>
      </b-tab>
      <b-tab title="Tilknytning" v-if="tabs.association">
        <employee-detail-association :uuid="uuid"/>
      </b-tab>
      <b-tab title="Orlov" v-if="tabs.leave">
        <employee-detail-leave :uuid="uuid"/>
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
  import EmployeeDetailAssociation from './EmployeeDetailAssociation'
  import EmployeeDetailLeave from './EmployeeDetailLeave'
  // import EmployeeDetailTable from './EmployeeDetailTable'
  import Loading from '../components/Loading'

  export default {
    components: {
      EmployeeDetailEngagement,
      EmployeeDetailContact,
      EmployeeDetailRole,
      EmployeeDetailIt,
      EmployeeDetailAssociation,
      EmployeeDetailLeave,
      // EmployeeDetailTable,
      Loading
    },
    props: {
      uuid: String
    },
    data () {
      return {
        tabs: {},
        isLoading: false,
        details: {}
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

      // this will be very smart at some point! We can essentially remove all table views
      // populateTables () {
      //   let vm = this
      //   vm.isLoading = true
      //   Employee.getDetailList(this.uuid)
      //   .then(detail => {
      //     let asyncArray = []
      //     for (let key in detail) {
      //       if (detail[key]) {
      //         asyncArray.push(key)
      //       }
      //     }
      //     asyncArray.forEach((element, index) => {
      //       Employee.getDetail(vm.uuid, element)
      //       .then(facet => {
      //         vm.details[asyncArray[index]] = facet
      //       })
      //     })
      //   })
      // }
    }
  }
</script>
i