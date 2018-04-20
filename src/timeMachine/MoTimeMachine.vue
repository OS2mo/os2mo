<template>
  <div>
    <h1>Tidsmaskinen</h1>
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
import MoTimeMachineColumn from './MoTimeMachineColumn'

export default {
  name: 'MoTimeMachine',
  components: {
    MoTimeMachineColumn
  }
}
</script>
