<template>
  <div class="row">
    <div class="col-sm-12 col-md-4 col-lg-4 col-xl-3">
      <div class="card">
        <div class="card-body d-flex flex-column">
          <h4 class="card-title">
            <icon name="folder-open"/>
            {{$t('common.overview')}}
          </h4>

          <div id="tree-wrapper">
            <mo-tree-view :org-uuid="orgUuid" linkable/>
          </div>
        </div>
      </div>
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
  import MoOrganisationUnitWorkflows from '@/organisation/MoOrganisationUnitWorkflows/MoOrganisationUnitWorkflows'
  import MoLog from '@/components/MoLog/MoLog'
  import MoTreeView from '@/components/MoTreeView/MoTreeView'
  import { mapGetters } from 'vuex'

  export default {
    components: {
      MoOrganisationUnitWorkflows,
      MoLog,
      MoTreeView
    },

    computed: {
      /**
       * Get organisation uuid.
       */
      ...mapGetters({
        orgUuid: 'organisation/getUuid'
      })
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

  .card-body {
    min-height: 5vh;
    max-height: 90vh;
    width: 100%;
  }

  #tree-wrapper {
    height: 100%;
    overflow-x: auto;
    overflow-y: scroll;
  }
</style>
