SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <mo-input-select
    class="col"
    v-model="internalValue"
    :label="labelText"
    :options="sortedOptions"
    :required="required"
    :disabled="disabled"
  />
</template>

<script>
/**
 * A facet picker component.
 */

import sortBy from "lodash.sortby"
import { MoInputSelect } from "@/components/MoInput"
import { Facet } from "@/store/actions/facet"

export default {
  name: "MoFacetPicker",

  components: {
    MoInputSelect,
  },

  props: {
    value: Object,
    facet: { type: String, required: true },
    required: Boolean,
    disabled: { type: Boolean, default: false },
    filter_function: { type: Function, default: null },
  },

  data() {
    return {
      internalValue: null,
    }
  },

  computed: {
    facetData() {
      return this.$store.getters[Facet.getters.GET_FACET](this.facet)
    },
    classData() {
      let class_data = this.facetData.classes
      if (this.filter_function) {
        return this.filter_function(class_data)
      }
      return class_data
    },
    sortedOptions() {
      return sortBy(this.classData, "name")
    },
    labelText() {
      return this.facetData.user_key
        ? this.$t(`input_fields.${this.facetData.user_key}`)
        : ""
    },
  },

  watch: {
    /**
     * Whenever selected change, update val.
     */
    internalValue(val) {
      this.$emit("input", val)
    },
  },

  created() {
    this.$store.dispatch(Facet.actions.SET_FACET, { facet: this.facet })
  },

  mounted() {
    if (this.value) {
      let filteredValue = this.value

      // This corresponds to the keys in the objects in the facet picker.
      const wantedKeys = ["example", "name", "owner", "scope", "user_key", "uuid"]

      // We sort out all keys not in the facet picker objects, otherwise it
      // is not able to recognize a pre-selected value
      for (const key of Object.keys(this.value)) {
        if (!wantedKeys.includes(key)) {
          delete filteredValue[key]
        }
      }

      this.internalValue = filteredValue
    }
  },
}
</script>
