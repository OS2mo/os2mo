<template>
  <div class="wrapper">
    <div 
      class="alert alert-success mt-2" 
      v-for="log in reverse(worklogs)" 
      v-bind:key="log.value" 
      role="alert"
    >
      {{$t('alerts.success.' + log.type, {uuid: log.value})}}
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'

  export default {
    name: 'MoWorklog',

    computed: {
      ...mapGetters({
        worklogs: 'log/getWorkLog'
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
