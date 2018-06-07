<template>
<div class="card card-margin">
  <div class="card-body">
    <h5>{{label}}</h5>
    <mo-worklog/>
    <!-- <b-tabs>
      <b-tab :title="$t('tabs.log.worklog')" active> 
        <mo-worklog/>
      </b-tab>
      <b-tab :title="$t('tabs.log.events')">
        {{$t('tabs.log.events')}}
      </b-tab>
      <b-tab :title="$t('tabs.log.errors')">
        <mo-errors/>
      </b-tab>
    </b-tabs> -->
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
  },
  data () {
    return {
      label: 'Arbejdslog'
    }
  }
}
</script>

<style scoped>
  .card-margin {
    margin-top: 2em;
    min-height: 150px;
  }
</style>
