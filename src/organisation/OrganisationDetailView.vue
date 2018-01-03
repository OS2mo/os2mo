<template>
  <div>
    <div class="headline">
      Enhed
    </div>
    <organisation-detail-unit/>
    <div class="headline">
      Lokation
    </div>
    <organisation-detail-location/>
    <div class="headline">
      Kontaktkanal
    </div>
    <organisation-detail-contact/>
  </div>
</template>

<script>
  import OrganisationDetailUnit from './OrganisationDetailUnit.vue'
  import OrganisationDetailLocation from './OrganisationDetailLocation.vue'
  import OrganisationDetailContact from './OrganisationDetailContact.vue'

  export default {
    components: {
      OrganisationDetailUnit,
      OrganisationDetailLocation,
      OrganisationDetailContact
    },
    data () {
      return {}
    },
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .headline {
    background-color: #007bff;
    color: white;
    padding-left: 1em;
    font-weight: bold;
  }
</style>