<template>
  <div>
    <div id="workflows">
      <button-workflow label="Ny Medarbejder" icon="user-plus" v-b-modal.employeeCreate/>
      <button-workflow label="Orlov" icon="user-md" target="EmployeeLeave"/>
      <button-workflow label="Flyt engagement" icon="share-square-o" target="EmployeeMove" v-b-modal.employeeMove/>
      <button-workflow label="Flyt mange engagementer" icon="share-square-o" target="EmployeeMoveMany"/>
      <button-workflow label="Afslut medarbejder" icon="user-times" target="EmployeeEnd" v-b-modal.employeeEnd/>
    </div>
    <!-- Modal Component -->
    <employee-create :org="org"/>
    <employee-move :org="org"/>
    <employee-end/>
  </div>
</template>

<script>
  import { EventBus } from '../EventBus'
  import ButtonWorkflow from '../components/ButtonWorkflow'
  import EmployeeCreate from './EmployeeCreate'
  import EmployeeMove from './EmployeeMove'
  import EmployeeEnd from './EmployeeEnd'

  export default {
    components: {
      ButtonWorkflow,
      EmployeeCreate,
      EmployeeMove,
      EmployeeEnd
    },
    data () {
      return {
        org: {}
      }
    },
    mounted () {
      EventBus.$on('organisation-changed', (org) => {
        this.org = org
      })
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