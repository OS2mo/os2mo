<template>
  <div>
    <div class="form-row">
      <mo-it-system-picker
        class="select-itSystem"
        v-model="entry.itsystem"
        :preselected="entry.itsystem && entry.itsystem.uuid"
      />

      <mo-input
        class="input-itSystem"
        v-model="entry.user_key"
        :label="$t('input_fields.account_name')"
        required
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
import MoInput from '@/components/atoms/MoInput'

export default {
  components: {
    MoInput,
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
        this.$emit('input', newVal)
      },
      deep: true
    }
  },

  computed: {
    nameId () {
      return 'mo-itsystem-' + this._uid
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
