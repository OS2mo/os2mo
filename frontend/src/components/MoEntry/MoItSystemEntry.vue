<template>
  <div>
    <div class="form-row">
      <mo-it-system-picker 
        class="select-itSystem" 
        v-model="entry.itsystem" 
        :preselected="entry.uuid"
      />
    </div>

    <mo-date-picker-range 
      v-model="entry.validity" 
      :initially-hidden="validityHidden"
    />
  </div>
</template>

<script>
  /**
   * A it system entry component.
   */

  import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
  import MoItSystemPicker from '@/components/MoPicker/MoItSystemPicker'

  export default {
    components: {
      MoDatePickerRange,
      MoItSystemPicker
    },

    props: {
      /**
       * Create two-way data bindings with the component.
       */
      value: Object,

      /**
       * This boolean property hides validity.
       */
      validityHidden: Boolean
    },

    data () {
      return {
        /**
         * The entry component value.
         * Used to detect changes and restore the value.
         */
        entry: {
          validity: {}
        }
      }
    },

    watch: {
      /**
       * Whenever entry change, update newVal.
       */
      entry: {
        handler (newVal) {
          newVal.type = 'it'
          if (newVal.itsystem !== undefined) newVal.uuid = newVal.itsystem.uuid
          this.$emit('input', newVal)
        },
        deep: true
      }
    },

    created () {
      /**
       * Called synchronously after the instance is created.
       * Set entry to value.
       */
      this.entry = this.value
    }
  }
</script>

