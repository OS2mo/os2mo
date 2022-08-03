SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group col">
    <label>{{ $tc("shared.engagement", 2) }}</label>
    <mo-loader v-show="isLoading" />

    <select
      :name="nameId"
      :id="nameId"
      :ref="nameId"
      :data-vv-as="$tc('shared.engagement', 2)"
      v-show="!isLoading"
      class="form-control col"
      v-model="selected"
      @change="updateSelectedEngagement()"
      :disabled="!employeeDefined"
      v-validate="{ required: true }"
    >
      <option disabled>{{ $tc("shared.engagement", 2) }}</option>
      <option v-for="e in orderedListOptions" :key="e.uuid" :value="e">
        {{ e.job_function.name }}, {{ e.org_unit.name }}
      </option>
    </select>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
/**
 * A engagement picker component.
 */

import Employee from "@/api/Employee"
import MoLoader from "@/components/atoms/MoLoader"

export default {
  name: "MoEngagementPicker",

  components: {
    MoLoader,
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * Defines a required employee.
     */
    employee: {
      required: true,
    },

    /**
     * This boolean property requires a selected name.
     */
    required: Boolean,
  },

  data() {
    return {
      /**
       * The selected, engagements, isLoading component value.
       * Used to detect changes and restore the value.
       */
      selected: null,
      engagements: [],
      isLoading: false,
    }
  },

  computed: {
    /**
     * Get name `engagement-picker`
     */
    nameId() {
      return "engagement-picker-" + this._uid
    },

    /**
     * Set employee as required.
     */
    isRequired() {
      if (!this.employeeDefined) return false
      return this.required
    },

    /**
     * If employee is not defined, return false and disable.
     */
    employeeDefined() {
      for (let key in this.employee) {
        if (this.employee.hasOwnProperty(key)) {
          return true
        }
      }
      return false
    },

    orderedListOptions() {
      return this.engagements.slice().sort((a, b) => {
        if (
          a.job_function.name &&
          a.org_unit.name < b.job_function.name &&
          b.org_unit.name
        ) {
          return -1
        }
        if (
          a.job_function.name &&
          a.org_unit.name > b.job_function.name &&
          b.org_unit.name
        ) {
          return 1
        }
        return 0
      })
    },
  },

  /**
   * Whenever employee change, get engagements.
   */
  watch: {
    employee() {
      this.getEngagements()
    },
  },

  mounted: function () {
    this.getEngagements()
    if (this.value) {
      this.selected = this.value
    }
  },

  methods: {
    /**
     * Get engagement details.
     */
    getEngagements() {
      if (this.employeeDefined) {
        let vm = this
        vm.isLoading = true
        Employee.getEngagementDetails(this.employee.uuid).then((response) => {
          vm.isLoading = false
          vm.engagements = response
        })
      }
    },

    /**
     * Update selected engagement.
     */
    updateSelectedEngagement() {
      this.$emit("input", this.selected)
    },
  },
}
</script>
