SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      class="address-date"
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{ orgUnitValidity, disabledDates }"
    />
    <div class="form-row">
      <mo-facet-picker
        class="form-group col"
        facet="visibility"
        v-model="entry.visibility"
      />
    </div>
    <div class="form-row">
      <mo-facet-picker
        class="col"
        :facet="facet"
        v-model="entry.address_type"
        required
      />

      <div class="form-group col">
        <div v-if="entry.address_type">
          <mo-address-search
            v-if="isDarAddress"
            :label="entry.address_type.name"
            v-model="address"
            required
          />
          <label :for="identifier" v-if="!isDarAddress">{{
            entry.address_type.name
          }}</label>
          <textarea
            :name="identifier"
            :id="identifier"
            v-if="!isDarAddress && isMultiLineText"
            :data-vv-as="entry.address_type.name"
            v-model.trim="contactInfo"
            type="text"
            class="form-control"
            v-validate="{ required: true, address: this.entry.address_type }"
          >
          </textarea>
          <textarea
            :name="identifier"
            :id="identifier"
            v-if="!isDarAddress && isMultiFieldText"
            :data-vv-as="entry.address_type.name"
            v-model.trim="contactInfo2"
            type="text"
            class="form-control"
            v-validate="{ required: false, address: this.entry.address_type }"
          >
          </textarea>
          <input
            :name="identifier"
            :id="identifier"
            v-if="!isDarAddress && !isMultiLineText"
            :data-vv-as="entry.address_type.name"
            v-model.trim="contactInfo"
            type="text"
            class="form-control"
            v-validate="{ required: true, address: this.entry.address_type }"
          />
        </div>
        <span v-show="errors.has(identifier)" class="text-danger">
          {{ errors.first(identifier) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * A address entry component.
 */

import MoAddressSearch from "@/components/MoAddressSearch"
import MoFacetPicker from "@/components/MoPicker/MoFacetPicker"
import { MoInputDateRange } from "@/components/MoInput"
import MoEntryBase from "./MoEntryBase"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,
  name: "MoAddressEntry",

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  components: {
    MoAddressSearch,
    MoFacetPicker,
    MoInputDateRange,
  },

  props: {
    /**
     * This boolean property requires a selected address type.
     * @type {Boolean}
     */
    required: Boolean,

    /**
     * Defines a label.
     * @type {String}
     */
    label: String,

    /**
     * The facet of the addresses.
     * @type {String}
     */
    facet: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      /**
       * The contactInfo, entry, address, addressScope component value.
       * Used to detect changes and restore the value.
       */
      contactInfo: "",
      contactInfo2: "",
      entry: {},
      address: null,
      addressScope: null,
    }
  },

  computed: {
    /**
     * If the address is a DAR.
     * @type {Boolean}
     */
    isDarAddress() {
      if (this.entry.address_type != null)
        return this.entry.address_type.scope === "DAR"
      return false
    },

    /**
     * If the address is a PHONE.
     * @type {Boolean}
     */
    isPhone() {
      if (this.entry.address_type != null)
        return this.entry.address_type.scope === "PHONE"
      return false
    },

    /**
     * If the address requires multi-line input (textarea)
     * @type {Boolean}
     */
    isMultiLineText() {
      return (
        this.entry.address_type != null &&
        (this.entry.address_type.scope === "TEXT" ||
          this.entry.address_type.scope === "MULTIFIELD_TEXT")
      )
    },

    /**
     * If the address requires multi-field input (textarea)
     * @type {Boolean}
     */
    isMultiFieldText() {
      return (
        this.entry.address_type != null &&
        this.entry.address_type.scope === "MULTIFIELD_TEXT"
      )
    },

    /**
     * Every scopes validity rules.
     */
    validityRules() {
      return {
        required: true,
        address: this.entry.address_type,
      }
    },
  },

  watch: {
    /**
     * Whenever contactInfo change, update entry with a Array.
     */
    contactInfo: {
      handler(newValue) {
        this.entry.type = "address"
        this.entry.value = newValue
        this.$emit("input", this.entry)
      },
    },

    contactInfo2: {
      handler(newValue) {
        this.entry.type = "address"
        this.entry.value2 = newValue
        this.$emit("input", this.entry)
      },
    },

    /**
     * When entry change, update the newVal.
     */
    entry: {
      handler(newVal) {
        newVal.type = "address"
        newVal.org = this.$store.getters["organisation/GET_ORGANISATION"]
        this.$emit("input", newVal)
      },
      deep: true,
    },

    /**
     * Whenever address change, update.
     */
    address: {
      handler(val) {
        if (val == null) return
        if (this.entry.address_type.scope === "DAR") {
          this.entry.value = val.location.uuid
        }
      },
      deep: true,
    },
  },

  created() {
    /**
     * Called synchronously after the instance is created.
     * Set entry and contactInfo to value.
     */
    if (this.value.value) {
      this.address = {
        location: {
          name: this.value.name,
          uuid: this.value.value,
        },
      }
      this.contactInfo = this.value.value
      this.contactInfo2 = this.value.value2
    }
    this.entry = this.value
  },
}
</script>
