<template>
  <div class="wrapper">
    <div 
      class="alert alert-danger" 
      v-for="log in reverse(workLogs)" 
      v-bind:key="log.uuid" 
      role="alert"
    >
      <span class="badge badge-light">{{log.data.status}}</span>
      {{log.data.message}}
    </div>
  </div>
</template>

<script>
  import { EventBus } from '@/EventBus'
  export default {
    name: 'MoError',

    data () {
      return {
        workLogs: []
      }
    },
    mounted () {
      EventBus.$on('mo-error', error => {
        this.workLogs.push(error)
      })
    },
    methods: {
      reverse (array) {
        return array.length ? array.slice().reverse() : array
      }
    }
  }
</script>

<style scoped>
.wrapper {
  max-height: 10rem;
  overflow-y: auto;
}
</style>
