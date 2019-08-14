<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
      :disable-to-date="!creatingDate"
      :disabled-dates="{orgUnitValidity, disabledDates}"
    />

    <div class="form-row">
      <mo-input-text
        :label="$t('input_fields.name')"
        v-model="entry.name"
        required
      />

      <mo-facet-picker
        facet="org_unit_type"
        v-model="entry.org_unit_type"
        required
      />

      <mo-facet-picker
        facet="time_planning"
        v-model="entry.time_planning"
        required
      />
    </div>

    <mo-organisation-unit-picker
      v-model="entry.parent"
      :label="$t('input_fields.select_super_unit')"
      required
      :validity="entry.validity"
    />
  </div>
</template>

<script>
/**
 * A organisation unit entry component.
 */
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import { MoInputText, MoInputDateRange } from '@/components/MoInput'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,

  name: 'MoOrganisationUnitEntry',

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoInputText
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
     * This boolean property able the date in create organisation component.
     */
    creatingDate: Boolean
  },

  computed: {
    orgUnitValidity () {
      if (this.entry.parent) {
        return this.entry.parent.validity
      }
      return this.disabledDates
    }
  },

  watch: {
    /**
     * Whenever orgUnit change, update newVal.
     */
    entry: {
      handler (newVal) {
        this.$emit('input', newVal)
      },
      deep: true
    }
  }
}
</script>
