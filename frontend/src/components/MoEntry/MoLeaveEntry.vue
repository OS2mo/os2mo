<template>
  <div>
    <div class="form-row">
      <mo-facet-picker
        facet="leave_type"
        v-model="entry.leave_type"
        required
      />
    </div>

    <mo-date-picker-range
      v-model="entry.validity"
      :initially-hidden="datePickerHidden"
    />
  </div>
</template>

<script>
/**
   * A leave entry component.
   */

import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    MoFacetPicker
  },

  props: {
    /**
       * Create two-way data bindings with the component.
       */
    value: Object,

    /**
       * Defines the validity.
       */
    validity: Object
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

  computed: {
    /**
       * Hides the validity.
       */
    datePickerHidden () {
      return this.validity != null
    }
  },

  watch: {
    /**
       * Whenever entry change, update newVal.
       */
    entry: {
      handler (newVal) {
        newVal.type = 'leave'
        this.$emit('input', newVal)
      },
      deep: true
    },

    /**
       * When validity change, update newVal.
       */
    validity (newVal) {
      this.entry.validity = newVal
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
