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
      <b-tab title="Engagementer">
        <organisation-detail-engagement :uuid="uuid"/>
      </b-tab>
    </b-tabs>
  </div>
</template>


<script>
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
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>