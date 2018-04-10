<template>
  <div 
    v-shortkey="{employeeCreate: ['ctrl', 'alt', 'n'], 
    employeeLeave: ['ctrl', 'alt', 'o'], 
    employeeMove: ['ctrl', 'alt', 'm'], 
    employeeMoveMany: ['ctrl', 'alt', 'y'],
    employeeTerminate: ['ctrl', 'alt', 'd']}" 
    @shortkey="shortcuts()"
  >
    <div id="workflows">
      <button-workflow label="Ny Medarbejder" icon="user-plus" v-b-modal.employeeCreate/>
      <button-workflow label="Orlov" icon="user-md" v-b-modal.employeeLeave/>
      <button-workflow label="Flyt engagement" icon="share-square-o" v-b-modal.employeeMove/>
      <button-workflow label="Flyt mange engagementer" icon="share-square-o" v-b-modal.employeeMoveMany/>
      <button-workflow label="Afslut medarbejder" icon="user-times" v-b-modal.employeeTerminate/>
    </div>

    <!-- Modal Component -->
    <mo-employee-create/>
    <mo-employee-leave/>
    <mo-employee-move/>
    <mo-employee-move-many/>
    <mo-employee-terminate/>
  </div>
</template>

<script>
  import ButtonWorkflow from '../../components/ButtonWorkflow'
  import MoEmployeeCreate from './MoEmployeeCreate'
  import MoEmployeeLeave from './MoEmployeeLeave'
  import MoEmployeeMove from './MoEmployeeMove'
  import MoEmployeeMoveMany from './MoEmployeeMoveMany'
  import MoEmployeeTerminate from './MoEmployeeTerminate'

  export default {
    components: {
      ButtonWorkflow,
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  #workflows {
    position: fixed;
    right: -240px;
    top: 100px;
    z-index: 1;
  }
</style>
