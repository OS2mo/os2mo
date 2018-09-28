<template>
  <div v-if="!removed">
    <div class="row">
      <div class="col">
        <component 
          :is="entryComponent"
          v-model="entryValue"
          :validity-hidden="validityHidden"
        />
      </div>

      <div class="col-1 v-center">
        <button @click="remove()" type="button" class="btn btn-outline-danger" :class="smallButtons ? 'btn-sm' : ''">
          <icon name="minus"/>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
  /**
   * A removable component.
   */

  export default {
    props: {
      /**
       * Create two-way data bindings with the component.
       */
      value: Object,

      /**
       * This boolean property defines the entry.
       */
      entryComponent: {
        type: Object,
        required: true
      },

      /**
       * This boolean property defines smallButtons.
       */
      smallButtons: Boolean,

      /**
       * This boolean property hides the validity.
       */
      validityHidden: Boolean
    },

    data () {
      return {
      /**
        * The entryValue, removed component value.
        * Used to detect changes and restore the value.
        */
        entryValue: {},
        removed: false
      }
    },

    updated () {
      /**
       * Called after data change.
       * Update entryValue.
       */
      this.$emit('input', this.entryValue)
    },

    created () {
      /**
       * Called synchronously after the instance is created.
       * Set entryValue to value.
       */
      this.entryValue = this.value
    },

    methods: {
      /**
       * Remove a entryValue.
       */
      remove () {
        this.entryValue = {}
        this.removed = true
      }
    }
  }
</script>

<style scoped>
  .v-center {
    margin-bottom: auto;
    margin-top: auto;
  }
</style>
