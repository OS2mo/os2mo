<template>
  <div :id="identifier">
    <div class="form-row">
      <mo-it-system-picker
        class="select-itSystem"
        v-model="entry.itsystem"
        :preselected="entry.itsystem && entry.itsystem.uuid"
      />

      <mo-input-text
        class="input-itSystem"
        v-model="entry.user_key"
        :label="$t('input_fields.account_name')"
        required
        />
    </div>

    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="disabledDates"
    />
  </div>
</template>

<script>
/**
 * A it system entry component.
 */
import MoItSystemPicker from '@/components/MoPicker/MoItSystemPicker'
import { MoInputText, MoInputDateRange } from '@/components/MoInput'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,
  name: 'MoItSystemEntry',
  components: {
    MoInputText,
    MoInputDateRange,
    MoItSystemPicker
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
  }
}
</script>
