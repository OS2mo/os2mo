<template>
  <div class="row">
    <div class="col-md-3">
      <the-left-menu/>
    </div>
    <div class="col-md-9 workflow-padding">
      <router-view :key="$route.params.uuid"/>
      <mo-log/>
    </div>
    <mo-organisation-unit-workflows/>
  </div>
</template>

<script>
  import TheLeftMenu from '@/components/TheLeftMenu'
  import MoOrganisationUnitWorkflows from '@/organisation/MoOrganisationUnitWorkflows/MoOrganisationUnitWorkflows'
  import MoLog from '@/components/MoLog/MoLog'

  export default {
    components: {
      TheLeftMenu,
      MoOrganisationUnitWorkflows,
      MoLog
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

  @media (min-width: 768px) {
   .workflow-padding {
    padding-right: 75px;
    }
  }

  @media (max-width: 768px) {
   .workflow-padding {
    padding-top: 30px;
    }
  }

</style>
