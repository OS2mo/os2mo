SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group col">
    <label :for="nameId">{{ $tc("shared.it_account", 1) }}</label>

    <select
      :name="nameId"
      :id="nameId"
      :data-vv-as="$tc('shared.it_account', 1)"
      class="form-control col"
      v-model="selected"
      @change="updateSelectedItAccount()"
      v-validate="{ required: true }"
    >
      <option disabled>{{ $tc("shared.it_account", 2) }}</option>
      <option v-for="it in orderedListOptions" v-bind:key="it.uuid" :value="it.uuid">
        {{ it.itsystem.name }} : {{ it.user_key }}
      </option>
    </select>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
/**
 * A picker for employee it accounts.
 */

import sortBy from "lodash.sortby"
import EmployeeApi from "@/api/Employee"

export default {
  name: "MoItAccountPicker",

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: [Object, Array],
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  data() {
    return {
      /**
       * The selected, IT accounts component value.
       * Used to detect changes and restore the value.
       */
      selected: {},
      itAccounts: [],
    }
  },

  computed: {
    /**
     * Get name `it-account-picker`.
     */
    nameId() {
      return "it-account-picker-" + this._uid
    },

    orderedListOptions() {
      return sortBy(this.itAccounts, "user_key")
    },
  },

  created() {
    /**
     * Called synchronously after the instance is created.
     * Set selected to preselected value.
     */
    if (this.value) {
      this.selected = this.value[0].uuid
    }
    this.getItAccounts()
  },

  methods: {
    /**
     * Get it systems.
     */
    getItAccounts() {
      var vm = this
      let employee = this.$store.state.employee
      EmployeeApi.getDetail(employee.uuid, "it", employee.validity).then((response) => {
        vm.itAccounts = response
      })
    },

    /**
     * Update selected it system data.
     */
    updateSelectedItAccount() {
      let data = {
        uuid: this.selected,
      }
      this.$emit("input", data)
    },
  },
}
</script>
