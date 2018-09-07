<template>
  <div 
    v-shortkey="{orgUnitCreate: ['ctrl', 'shift', 'c'], 
    orgUnitRename: ['ctrl', 'shift', 'r'], 
    orgUnitMove: ['ctrl', 'shift', 'm'], 
    orgUnitTerminate: ['ctrl', 'shift', 'd']}" 
    @shortkey="theAction($event)"
  >
    <mo-workflow>
      <mo-workflow-button 
        class="btn-unit-create" 
        :label="$t('workflows.organisation.create_unit')" 
        icon="plus-circle" 
        v-b-modal.orgUnitCreate
      />

      <mo-workflow-button 
        class="btn-unit-rename" 
        :label="$t('workflows.organisation.rename_unit')" 
        icon="edit" 
        v-b-modal.orgUnitRename
      />

      <mo-workflow-button 
        class="btn-unit-move" 
        :label="$t('workflows.organisation.move_unit')" 
        icon="share-square" 
        v-b-modal.orgUnitMove
      />

      <mo-workflow-button 
        class="btn-unit-terminate" 
        :label="$t('workflows.organisation.terminate_unit')" 
        icon="ban" 
        v-b-modal.orgUnitTerminate
      />
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
      theAction (event) {
        this.$root.$emit('bv::show::modal', event.srcKey)
      }
    }
  }
</script>
