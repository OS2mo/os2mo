SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <span>
    <mo-loader v-show="isLoading" />

    <p class="col no-address" v-show="!isLoading && noAddresses && orgUnit">
      {{ $t("input_fields.no_addresses_associated_to_org_unit") }}
    </p>

    <div class="form-group" v-show="!isLoading && !noAddresses">
      <label :for="nameId">{{ label }}</label>
      <select
        class="form-control col"
        v-model="selected"
        :name="nameId"
        :id="nameId"
        data-vv-as="Adresser"
        :disabled="isDisabled"
        :noAddresses="noAddresses"
        @change="updateSelectedAddress()"
      >
        <option disabled>{{ label }}</option>
        <option v-for="a in orderedListOptions" :key="a.uuid" :value="a">
          ({{ a.address_type.name }}) {{ a.name }}
        </option>
      </select>
    </div>
  </span>
</template>

<script>
/**
 * A address picker component.
 */
import sortBy from "lodash.sortby"
import OrganisationUnit from "@/api/OrganisationUnit"
import MoLoader from "@/components/atoms/MoLoader"

export default {
  name: "AddressPicker",

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  components: {
    MoLoader,
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * Defines a orgUnit.
     */
    orgUnit: {
      type: Object,
    },
  },

  data() {
    return {
      /**
       * The label component value.
       * Used to set a default value.
       */
      label: "Adresser",

      /**
       * The selected, addresses, isLoading component value.
       * Used to detect changes and restore the value.
       */
      selected: {},
      addresses: [],
      isLoading: false,
    }
  },

  computed: {
    /**
     * Get name `mo-address-picker`.
     */
    nameId() {
      return "mo-address-picker-" + this._uid
    },

    /**
     * Disable orgUnit.
     */
    isDisabled() {
      return this.orgUnit == null
    },

    /**
     * Return blank address.
     */
    noAddresses() {
      return this.addresses.length === 0
    },

    orderedListOptions() {
      return sortBy(this.addresses, "address_type.name")
    },
  },

  watch: {
    /**
     * Whenever orgUnit change, get addresses.
     */
    orgUnit() {
      this.getAddresses()
    },
  },

  /**
   * Called after the instance has been mounted.
   * Get addresses and set selected as value.
   */
  mounted() {
    this.getAddresses()
    this.selected = this.value
  },

  methods: {
    /**
     * Get organisation unit address details.
     */
    getAddresses() {
      if (this.orgUnit == null) return
      let vm = this
      vm.isLoading = true
      OrganisationUnit.getAddressDetails(this.orgUnit.uuid).then((response) => {
        vm.isLoading = false
        vm.addresses = response
      })
    },

    /**
     * Update selected address.
     */
    updateSelectedAddress() {
      this.$emit("input", this.selected)
    },
  },
}
</script>

<style scoped>
.no-address {
  margin-top: 2.5rem;
  opacity: 0.5;
  font-style: italic;
}
</style>
