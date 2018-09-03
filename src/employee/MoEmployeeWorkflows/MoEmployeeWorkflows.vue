<template>
  <div 
    v-shortkey="{employeeCreate: ['ctrl', 'alt', 'n'], 
    employeeLeave: ['ctrl', 'alt', 'o'], 
    employeeMove: ['ctrl', 'alt', 'm'], 
    employeeMoveMany: ['ctrl', 'alt', 'y'],
    employeeTerminate: ['ctrl', 'alt', 'd']}" 
    @shortkey="shortcuts()"
  >
    <mo-workflow>
      <mo-workflow-button 
        class="btn-employee-create" 
        :label="$t('workflows.employee.new_employee')" 
        icon="user-plus" 
        v-b-modal.employeeCreate
      />

      <mo-workflow-button 
        class="btn-employee-leave" 
        :label="$t('workflows.employee.leave')" 
        icon="user-md" 
        v-b-modal.employeeLeave
      />

      <mo-workflow-button 
        class="btn-employee-move" 
        :label="$t('workflows.employee.move_engagement')" 
        icon="user-tag" 
        v-b-modal.employeeMove
      />

      <mo-workflow-button 
        class="btn-employee-moveMany" 
        :label="$t('workflows.employee.move_many_engagements')" 
        icon="users" 
        v-b-modal.employeeMoveMany
      />

      <mo-workflow-button 
        class="btn-employee-terminate" 
        :label="$t('workflows.employee.terminate_employee')" 
        icon="user-times" 
        v-b-modal.employeeTerminate
      />
    </mo-workflow>

    <!-- Modal Components -->
    <mo-employee-create/>

    <mo-employee-leave/>

    <mo-employee-move/>

    <mo-employee-move-many/>

    <mo-employee-terminate/>
  </div>
</template>

<script>
  import MoWorkflow from '@/components/MoWorkflow/MoWorkflow'
  import MoWorkflowButton from '@/components/MoWorkflow/MoWorkflowButton'
  import MoEmployeeCreate from './MoEmployeeCreate'
  import MoEmployeeLeave from './MoEmployeeLeave'
  import MoEmployeeMove from './MoEmployeeMove'
  import MoEmployeeMoveMany from './MoEmployeeMoveMany'
  import MoEmployeeTerminate from './MoEmployeeTerminate'

  export default {
    components: {
      MoWorkflow,
      MoWorkflowButton,
      MoEmployeeCreate,
      MoEmployeeLeave,
      MoEmployeeMove,
      MoEmployeeMoveMany,
      MoEmployeeTerminate
    },

    methods: {
      shortcuts () {
        this.$root.$emit('bv::show::modal', event.srcKey)
      }
    }
  }
</script>

