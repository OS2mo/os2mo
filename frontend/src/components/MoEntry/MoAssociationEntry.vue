<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        class="col unit-association"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
      />

      <mo-address-picker
        class="col address-association"
        v-model="entry.address"
        :org-unit="entry.org_unit"
      />
    </div>

    <div class="form-row select-association">
      <mo-facet-picker
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

import { MoInputDateRange } from '@/components/MoInput'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoAddressPicker from '@/components/MoPicker/MoAddressPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'
import OrgUnitValidity from '@/mixins/OrgUnitValidity'

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: 'MoAssociationEntry',

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoAddressPicker,
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
