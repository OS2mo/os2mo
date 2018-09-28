<template>
  <div class="row">
    <div class="col-sm-12 col-md-4 col-lg-4 col-xl-3">
      <the-left-menu/>
    </div>

    <div class="col-sm-12 col-md-8 col-lg-8 col-xl-9 workflow-padding">
      <router-view :key="$route.params.uuid"/>

      <mo-log/>
    </div>

    <mo-organisation-unit-workflows/>
  </div>
</template>

<script>
  /**
   * A organisation component.
   */

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
