<template>
  <div class="wrapper">
    <div 
      class="alert alert-success mt-2" 
      v-for="(log, index) in reverse(worklogs)" 
      :key="index" 
      role="alert"
    >
      {{$t('alerts.success.' + log.type, {uuid: log.value})}}
    </div>
  </div>
</template>

<script>
  /**
   * A worklog component.
   */

  import { mapGetters } from 'vuex'

  export default {
    name: 'MoWorklog',

    computed: {
      /**
       * Get worklog message.
       */
      ...mapGetters({
        worklogs: 'log/getWorkLog'
      })
    },

    methods: {
      /**
       * Reverse message.
       */
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
