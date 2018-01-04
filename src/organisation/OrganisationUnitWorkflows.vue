<template>
  <div>
    <div id="workflows">
      <workflow-button label="Opret enhed" icon="plus-circle" v-b-modal.orgUnitCreate/>
      <workflow-button label="Omdøb enhed" icon="pencil-square-o" v-b-modal.orgUnitRename/>
      <workflow-button label="Flyt enhed" icon="share-square-o" v-b-modal.orgUnitMove/>
      <workflow-button label="Afslut enhed" icon="ban" v-b-modal.orgUnitEnd/>
    </div>
  <!-- Modal Component -->
  <b-modal id="orgUnitCreate" size="lg" hide-footer title="Opret enhed">
    <unit-create/>
  </b-modal>
  <b-modal id="orgUnitRename" size="lg" hide-footer title="Omdøb enhed">
    <unit-rename/>
  </b-modal>
  <b-modal id="orgUnitMove" size="lg" hide-footer title="Flyt enhed">
    <unit-move/>
  </b-modal>
  <b-modal id="orgUnitEnd" size="lg" hide-footer title="Afslut enhed">
    <unit-end/>
  </b-modal>
  </div>
</template>

<script>
  import WorkflowButton from '../components/WorkflowButton'
  import UnitCreate from './OrganisationUnitCreate'
  import UnitRename from './OrganisationUnitRename'
  import UnitMove from './OrganisationUnitMove'
  import UnitEnd from './OrganisationUnitEnd'

  export default {
    components: {
      WorkflowButton,
      UnitCreate,
      UnitRename,
      UnitMove,
      UnitEnd
    },
    data () {
      return {}
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  #workflows {
    position: absolute;
    right: -240px;
    top: 100px;
    z-index: 1;
  }
</style>