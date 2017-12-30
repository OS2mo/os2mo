<template>
    <div class="row">
    <div class="col-md-3">
      <the-left-menu/>
    </div>
    <div class="col-md-9 workflow-padding">
      <router-view/>
    </div>
    
    <employee-workflows/>
  </div>
</template>

<script>
  import TheLeftMenu from '../components/TheLeftMenu'
  import EmployeeWorkflows from './EmployeeWorkflows'

  export default {
    components: {
      TheLeftMenu,
      EmployeeWorkflows
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .workflow-padding {
    padding-right: 75px;
  }

</style>
