<template>
<div class="card card-margin">
  <div class="card-body">
    <b-tabs>
      <b-tab title="Arbejdslog" active> 
        <mo-worklog/>
      </b-tab>
      <b-tab title="Begivenheder">
        Begivenheder
      </b-tab>
      <b-tab title="Fejl">
        <mo-errors/>
      </b-tab>
    </b-tabs>
  </div>
</div>
</template>

<script>
  import MoWorklog from './MoWorklog'
  import MoErrors from './MoErrors'
  export default {
    name: 'MoLog',
    components: {
      MoWorklog,
      MoErrors
    }
  }
</script>

<style scoped>
  .card-margin {
    margin-top: 2em;
    min-height: 150px;
  }
</style>
