<template>
  <div 
    v-shortkey="{orgUnitCreate: ['ctrl', 'alt', 'n'], 
    orgUnitRename: ['ctrl', 'alt', 'r'], 
    orgUnitMove: ['ctrl', 'alt', 'm'], 
    orgUnitTerminate: ['ctrl', 'alt', 'd']}" 
    @shortkey="theAction()"
  >
    <mo-workflow>
      <mo-workflow-button :label="$t('workflows.organisation.create_unit')" icon="plus-circle" v-b-modal.orgUnitCreate/>
      <mo-workflow-button :label="$t('workflows.organisation.rename_unit')" icon="pencil-square-o" v-b-modal.orgUnitRename/>
      <mo-workflow-button :label="$t('workflows.organisation.move_unit')" icon="share-square-o" v-b-modal.orgUnitMove/>
      <mo-workflow-button :label="$t('workflows.organisation.terminate_unit')" icon="ban" v-b-modal.orgUnitTerminate/>
    </mo-workflow>

    <!-- Modal Component -->
    <mo-organisation-unit-create/>
    <mo-organisation-unit-rename/>
    <mo-organisation-unit-move/>
    <mo-organisation-unit-terminate/>
  </div>
</template>

<script>
  import MoWorkflowButton from '@/components/MoWorkflow/MoWorkflowButton'
  import MoWorkflow from '@/components/MoWorkflow/MoWorkflow'
  import MoOrganisationUnitCreate from './MoOrganisationUnitCreate'
  import MoOrganisationUnitRename from './MoOrganisationUnitRename'
  import MoOrganisationUnitMove from './MoOrganisationUnitMove'
  import MoOrganisationUnitTerminate from './MoOrganisationUnitTerminate'

  export default {
    components: {
      MoWorkflowButton,
      MoWorkflow,
      MoOrganisationUnitCreate,
      MoOrganisationUnitRename,
      MoOrganisationUnitMove,
      MoOrganisationUnitTerminate
    },
    methods: {
      theAction () {
        this.$root.$emit('bv::show::modal', event.srcKey)
      }
    }
  }
</script>
