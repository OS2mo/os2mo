<template>
  <div>
    <h1>{{$tc('common.time_machine', 2)}}</h1>

    <div class="row">
      <div class="col">
        <mo-time-machine-column store-id="$_timeMachineLeft"/>
      </div>

      <div class="col">
        <mo-time-machine-column store-id="$_timeMachineRight"/>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * A timemachine component.
 */

import MoTimeMachineColumn from './_components/MoTimeMachineColumn'

export default {
  name: 'MoTimeMachine',

  components: {
    MoTimeMachineColumn
  }
}
</script>
