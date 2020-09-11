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

    <div v-for="(dynamic, index) in dynamicFacets" :key="dynamic">
        <mo-recursive-facet-picker
          :label="facet_uuid_to_label(dynamic)"
          class="select-association"
          :facet_uuid="dynamic"
          v-bind:value="fetch_entry(dynamic)"
          v-on:input="set_entry($event, dynamic)"
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
import MoRecursiveFacetPicker from '@/components/MoPicker/MoRecursiveFacetPicker'
import MoEntryBase from './MoEntryBase'
import OrgUnitValidity from '@/mixins/OrgUnitValidity'
import { Employee } from '@/store/actions/employee'
import { mapGetters } from 'vuex'
import { Facet } from '@/store/actions/facet'

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
    },

    dynamicFacets () {
      let conf = this.$store.getters['conf/GET_CONF_DB']
      return conf.association_dynamic_facets.split(',').filter(elem => elem != "")
    },
  },

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoRecursiveFacetPicker,
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
  },

  methods: {
    /**
     * Find the first element in the array fulfilling the predicate
     * @param {Array} arr - Array to search for elements in
     * @param {Function} test - The predicate function to run against each element
     * @param {Any} ctx - Context to be passed through to the predicate
     * @returns {Any} the found element in the list or null
     */
    find(arr, test, ctx) {
      let result = null;
      arr.some(function(el, i) {
        return test.call(ctx, el, i, arr) ? ((result = el), true) : false;
      });
      return result;
    },

    /**
     * Fetch the relevant entry for the recursive picker.
     * @param {String} dynamic - Uuid facet for the picker
     * @returns {Any} the found element in the list or null
     */
    fetch_entry(dynamic) {
      // Ensure we have an array
      if (Array.isArray(this.entry.dynamic_classes) == false) {
        this.entry.dynamic_classes = []
      }
      // Find the correct element if it exists
      let entry = this.find(
        this.entry.dynamic_classes,
        item => { return item['top_level_facet']['uuid'] == dynamic}
      )
      return entry
    },

    /**
     * Set the relevant entry for the recursive picker.
     * NOTE: Currently only supports a single recursive picker.
     *
     * @param {Any} Event - The data coming out of the picker
     * @param {String} dynamic - Uuid facet for the picker
     * @returns {None}
     */
    set_entry(event, dynamic) {
      this.entry.dynamic_classes = [event]
    },

    /**
     * Lookup the description of the facet given by uuid.
     *
     * @param {String} dynamic - Uuid for facet to lookup
     * @returns {String} Description of the facet.
     */
    facet_uuid_to_label(uuid) {
      let facet_getter = this.$store.getters[Facet.getters.GET_FACET]
      return facet_getter(uuid)['description']
    }
  }
}
</script>
