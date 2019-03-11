<template>
  <div>
    <b-form-checkbox
      class="mb-3 mt-1"
      data-vv-as="checkbox"
      v-model="entry.primary">
      {{$t('input_fields.primary')}}
    </b-form-checkbox>

    <div class="form-row">
      <mo-organisation-unit-picker
        class="col unit-association"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
      />

      <mo-facet-picker
        class="select-association"
        facet="association_type"
        v-model="entry.association_type"
        required
      />
    </div>

    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{orgUnitValidity, disabledDates}"
    />
  </div>
</template>

<script>
/**
 * A association entry component.
 */

import bFormCheckbox from 'bootstrap-vue/es/components/form-checkbox/form-checkbox'
import { MoInputDateRange } from '@/components/MoInput'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'
import OrgUnitValidity from '@/mixins/OrgUnitValidity'

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: 'MoAssociationEntry',

  components: {
    bFormCheckbox,
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler (newVal) {
        newVal.type = 'association'
        this.$emit('input', newVal)
      },
      deep: true
    }
  }
}
</script>
