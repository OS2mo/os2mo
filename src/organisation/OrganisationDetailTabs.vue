<template>
  <div>
    <b-tabs>
      <b-tab title="Enhed" active> 
        <organisation-detail-unit :uuid="uuid"/>
      </b-tab>
      <b-tab title="Lokation">
        <organisation-detail-location :uuid="uuid"/>
      </b-tab>
      <b-tab title="Kontaktkanal">
        <organisation-detail-contact :uuid="uuid"/>
      </b-tab>
      <b-tab title="Engagementer" v-if="tabs.engagement">
        <organisation-detail-engagement :uuid="uuid"/>
      </b-tab>
      <b-tab title="Tilknytninger" v-if="tabs.association">
      </b-tab>
    </b-tabs>
  </div>
</template>


<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import OrganisationDetailUnit from './OrganisationDetailUnit'
  import OrganisationDetailLocation from './OrganisationDetailLocation'
  import OrganisationDetailContact from './OrganisationDetailContact'
  import OrganisationDetailEngagement from './OrganisationDetailEngagement'
  export default {
    components: {
      OrganisationDetailUnit,
      OrganisationDetailLocation,
      OrganisationDetailContact,
      OrganisationDetailEngagement
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
        OrganisationUnit.getDetailList(this.uuid)
        .then(respone => {
          this.tabs = respone
        })
      }
    }
  }
</script>
