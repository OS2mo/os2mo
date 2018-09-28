<template>
  <div class="wrapper">
    <div 
      class="alert alert-danger" 
      v-for="log in reverse(errors)" 
      v-bind:key="log.uuid" 
      role="alert"
    >
      <span class="badge badge-light">{{log.data.status}}</span>
      {{log.data.message}}
    </div>
  </div>
</template>

<script>
  /**
   * A error component.
   */

  import { mapGetters } from 'vuex'

  export default {
    name: 'MoError',

    computed: {
      /**
       * Get error message.
       */
      ...mapGetters({
        errors: 'log/getErrors'
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
