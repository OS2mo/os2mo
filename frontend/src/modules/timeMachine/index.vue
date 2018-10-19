<template>
  <div>
    <h1>{{$tc('shared.time_machine', 2)}}</h1>

    <div class="row">
      <div class="col">
        <mo-time-machine-column/>
      </div>

      <div class="col">
        <mo-time-machine-column/>
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
