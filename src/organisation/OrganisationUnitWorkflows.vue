<template>
  <div 
    v-shortkey="{orgUnitCreate: ['ctrl', 'alt', 'n'], 
    orgUnitRename: ['ctrl', 'alt', 'r'], 
    orgUnitMove: ['ctrl', 'alt', 'm'], 
    orgUnitTerminate: ['ctrl', 'alt', 'd']}" 
    @shortkey="theAction()"
  >
    <div id="workflows">
      <button-workflow label="Opret enhed" icon="plus-circle" v-b-modal.orgUnitCreate/>
      <button-workflow label="Omdøb enhed" icon="pencil-square-o" v-b-modal.orgUnitRename/>
      <button-workflow label="Flyt enhed" icon="share-square-o" v-b-modal.orgUnitMove/>
      <button-workflow label="Afslut enhed" icon="ban" v-b-modal.orgUnitTerminate/>
    </div>
  <!-- Modal Component -->
  <unit-create/>
  <unit-rename/>
  <unit-move/>
  <unit-end/>
  </div>
</template>

<script>
  import ButtonWorkflow from '@/components/ButtonWorkflow'
  import UnitCreate from './OrganisationUnitCreate'
  import UnitRename from './OrganisationUnitRename'
  import UnitMove from './OrganisationUnitMove'
  import UnitEnd from './OrganisationUnitEnd'

  export default {
    components: {
      ButtonWorkflow,
      UnitCreate,
      UnitRename,
      UnitMove,
      UnitEnd
    },
    data () {
      return {
        org: {}
      }
    },
    methods: {
      theAction () {
        this.$root.$emit('bv::show::modal', event.srcKey)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  #workflows {
    position: fixed;
    right: -240px;
    top: 100px;
    z-index: 1;
  }
</style>