<template>
  <div>
    <div class="form-row">
      <mo-facet-picker
        facet="leave_type"
        v-model="entry.leave_type"
        required
      />
    </div>

    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="datePickerHidden"
      :disabled-dates="disabledDates"
    />
  </div>
</template>

<script>
/**
 * A leave entry component.
 */

import { MoInputDateRange } from '@/components/MoInput'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,
  name: 'MoLeaveEntry',
  components: {
    MoInputDateRange,
    MoFacetPicker
  },

  props: {
    /**
     * Defines the validity.
     */
    validity: Object
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
  }
}
</script>
