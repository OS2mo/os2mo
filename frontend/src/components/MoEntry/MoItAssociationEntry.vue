SPDX-FileCopyrightText: 2018-2022 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      class="from-date"
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{ orgUnitValidity, disabledDates }"
    />

    <mo-employee-picker
      v-model="entry.person"
      class="search-employee mb-3"
      v-if="!hideEmployeePicker && hideOrgPicker"
      :label="$tc('input_fields.employee_optional')"
      :validity="entry.validity"
    />

    <div class="form-row employee_info">
      <mo-input-text
        :label="$tc('shared.employee')"
        v-if="hideEmployeePicker"
        v-model="entry.person.name"
        disabled
      />
    </div>

    <div class="form-row" style="align-items: flex-end">
      <mo-organisation-unit-picker
        v-if="!hideOrgPicker"
        class="col unit-association"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
        :validity="entry.validity"
        :extra-validations="validations"
      />

      <mo-it-account-picker class="select-itAccount" v-model="entry.it" required />

      <mo-input-primary-check class="col checkbox" v-model="entry.primary" />
    </div>

    <mo-facet-picker :facet="jobFunctionFacet" v-model="entry.job_function" required />
  </div>
</template>

<script>
/**
 * An IT association entry component.
 */

import MoInputPrimaryCheck from "@/components/MoInput/MoInputPrimaryCheck"
import MoItAccountPicker from "@/components/MoPicker/MoItAccountPicker"
import { MoInputDateRange, MoInputText } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoEmployeePicker from "@/components/MoPicker/MoEmployeePicker"
import MoFacetPicker from "@/components/MoPicker/MoFacetPicker"
import MoRecursiveFacetPicker from "@/components/MoPicker/MoRecursiveFacetPicker"
import MoEntryBase from "./MoEntryBase"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"
import { Employee } from "@/store/actions/employee"
import { mapGetters } from "vuex"
import { Facet } from "@/store/actions/facet"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: "MoItAssociationEntry",

  props: {
    /**
     * This boolean property hide the org picker.
     */
    hideOrgPicker: Boolean,

    /**
     * This boolean property hide the employee picker.
     */
    hideEmployeePicker: Boolean,
  },

  data: function () {
    return {
      primary_types: null,
    }
  },

  computed: {
    ...mapGetters({
      currentEmployee: Employee.getters.GET_EMPLOYEE,
    }),

    validations() {
      return {}
    },

    jobFunctionFacet() {
      // Ask backend if an "engagement_job_function_bvn" facet exists
      let facet = this.$store.getters[Facet.getters.GET_FACET](
        "engagement_job_function_bvn"
      )

      if (Object.keys(facet).length) {
        // If it does, it contains the user-facing job titles, and we should use it
        return "engagement_job_function_bvn"
      } else {
        // If not, we should use the regular job title classes instead
        return "engagement_job_function"
      }
    },
  },

  created() {
    if (
      !(this.entry.person && this.entry.person.name) &&
      this.currentEmployee &&
      this.currentEmployee.name
    ) {
      this.$set(this.entry, "person", this.currentEmployee)
    }
  },

  mounted() {
    // Dispatch backend request to check if facet "engagement_job_function_bvn" exists
    this.$store.dispatch(Facet.actions.SET_FACET, {
      facet: "engagement_job_function_bvn",
    })
  },

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoEmployeePicker,
    MoFacetPicker,
    MoRecursiveFacetPicker,
    MoInputText,
    MoItAccountPicker,
    MoInputPrimaryCheck,
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler(newVal) {
        newVal.type = "association"
        this.$emit("input", newVal)
      },
      deep: true,
    },
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
      let result = null
      arr.some(function (el, i) {
        return test.call(ctx, el, i, arr) ? ((result = el), true) : false
      })
      return result
    },

    /**
     * Fetch the relevant entry for the recursive picker.
     * @param {String} dynamic - Uuid facet for the picker
     * @returns {Any} the found element in the list or null
     */
    fetch_entry(dynamic) {
      // Ensure we have an array
      if (Array.isArray(this.entry.dynamic_classes) === false) {
        this.entry.dynamic_classes = []
      }
      // Find the correct element if it exists
      let entry = this.find(this.entry.dynamic_classes, (item) => {
        return item["top_level_facet"]["uuid"] === dynamic
      })
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
      return facet_getter(uuid)["description"]
    },
  },
}
</script>
