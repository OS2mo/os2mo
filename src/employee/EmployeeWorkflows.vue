<template>
  <div id="workflows">
    <workflow-button label="Ny Medarbejder" icon="user-plus" target="EmployeeCreate"/>
    <workflow-button label="Orlov" icon="user-md" target="EmployeeLeave"/>
    <workflow-button label="Flyt engagement" icon="share-square-o" target="EmployeeMove"/>
    <workflow-button label="Flyt mange engagementer" icon="share-square-o" target="EmployeeMoveMany"/>
    <workflow-button label="Afslut medarbejder" icon="user-times" target="EmployeeEnd"/>
  </div>
</template>

<script>
  import WorkflowButton from '../components/WorkflowButton'

  export default {
    components: {
      WorkflowButton
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