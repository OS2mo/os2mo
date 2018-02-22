<template>
  <div>
    <loading v-show="isLoading"/>
    <b-tabs v-show="!isLoading">
      <b-tab title="Engagement" active v-if="tabs.engagement"> 
        <mo-engagement-detail :uuid="uuid"/>
      </b-tab>
      <b-tab title="Adresser" v-if="tabs.address">
        <mo-address-detail :uuid="uuid"/>
      </b-tab>
      <b-tab title="Rolle" v-if="tabs.role">
        <mo-role-detail :uuid="uuid"/>
      </b-tab>
      <b-tab title="IT" v-if="tabs.it">
        <mo-it-system-detail :uuid="uuid"/>
      </b-tab>
      <b-tab title="Tilknytning" v-if="tabs.association">
        <mo-association-detail :uuid="uuid"/>
      </b-tab>
      <b-tab title="Orlov" v-if="tabs.leave">
        <mo-leave-detail :uuid="uuid"/>
      </b-tab>
    </b-tabs>
  </div>
</template>


<script>
  import Employee from '../api/Employee'
  import MoEngagementDetail from './MoEngagement/MoEngagementDetail'
  import MoAddressDetail from './MoAddress/MoAddressDetail'
  import MoRoleDetail from './MoRole/MoRoleDetail'
  import MoItSystemDetail from './MoItSystem/MoItSystemDetail'
  import MoLeaveDetail from './MoLeave/MoLeaveDetail'
  import MoAssociationDetail from './MoAssociation/MoAssociationDetail'
  import Loading from '../components/Loading'

  export default {
    components: {
      MoEngagementDetail,
      MoAddressDetail,
      MoRoleDetail,
      MoItSystemDetail,
      MoAssociationDetail,
      MoLeaveDetail,
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