SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      class="from-date"
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{orgUnitValidity, disabledDates}"
    />

    <div class="form-row">
      <mo-facet-picker v-if="showPrimary"
                       facet="primary_type"
                       v-model="entry.primary"
                       required
      />

      <mo-organisation-unit-picker
        class="col unit-association"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
        :validity="entry.validity"
        :extra-validations="validations"
      />

      <mo-facet-picker
        class="select-association"
        facet="association_type"
        v-model="entry.association_type"
        required
      />
    </div>
  </div>
</template>

<script>
/**
 * A association entry component.
 */

import { MoInputDateRange } from '@/components/MoInput'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'
import OrgUnitValidity from '@/mixins/OrgUnitValidity'
import { Employee } from '@/store/actions/employee'
import { mapGetters } from 'vuex'

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: 'MoAssociationEntry',

  computed: {
    ...mapGetters({
      currentEmployee: Employee.getters.GET_EMPLOYEE
    }),

    validations () {
      return {
        existing_associations: [
          this.currentEmployee,
          this.entry.org_unit,
          this.entry.validity,
          this.entry.uuid
        ]
      }
    },

    showPrimary () {
      let conf = this.$store.getters['conf/GET_CONF_DB']

      return conf.show_primary_association
    }
  },

  components: {
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
