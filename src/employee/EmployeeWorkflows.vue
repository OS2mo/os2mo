<template>
  <div>
    <div id="workflows">
      <button-workflow label="Ny Medarbejder" icon="user-plus" v-b-modal.employeeCreate/>
      <button-workflow label="Orlov" icon="user-md" target="EmployeeLeave"/>
      <button-workflow label="Flyt engagement" icon="share-square-o" target="EmployeeMove"/>
      <button-workflow label="Flyt mange engagementer" icon="share-square-o" target="EmployeeMoveMany"/>
      <button-workflow label="Afslut medarbejder" icon="user-times" target="EmployeeEnd"/>
    </div>
    <employee-create/>
  </div>
</template>

<script>
  import ButtonWorkflow from '../components/ButtonWorkflow'
  import EmployeeCreate from './EmployeeCreate'

  export default {
    components: {
      ButtonWorkflow,
      EmployeeCreate
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