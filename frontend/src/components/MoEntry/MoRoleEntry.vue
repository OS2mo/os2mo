<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        class="col unit-role"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
      />

      <mo-facet-picker
        class="select-role"
        facet="role_type"
        v-model="entry.role_type"
        required
      />
    </div>

    <mo-date-picker-range
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="disabledDates"
    />
  </div>
</template>

<script>
/**
 * A role entry component.
 */

import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,
  name: 'MoRoleEntry',
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoFacetPicker
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler (newVal) {
        newVal.type = 'role'
        this.$emit('input', newVal)
      },
      deep: true
    }
  }
}
</script>
