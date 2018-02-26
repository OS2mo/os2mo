<template>
    <div class="row">
    <div class="col-12 workflow-padding">
      <router-view :key="$route.params.uuid"/>
    </div>
    
    <mo-employee-workflows/>
  </div>
</template>

<script>
  import MoEmployeeWorkflows from './MoEmployeeWorkflows/MoEmployeeWorkflows'

  export default {
    components: {
      MoEmployeeWorkflows
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

  @media (min-width: 768px) {
   .workflow-padding {
    padding-right: 75px;
    }
   }

   @media (max-width: 768px) {
   .workflow-padding {
    padding-top: 30px;
    }
  }

</style>
