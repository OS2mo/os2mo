SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <mo-input-autocomplete
    v-model="internalValue"
    :label="label"
    :items="addressSuggestions"
    :get-label="getLabel"
    :component-item="template"
    @update-items="getGeographicalLocation"
    :required="isRequired"
  />
</template>

<script>
/**
 * Address search field component.
 */

import Search from "@/api/Search"
import "v-autocomplete/dist/v-autocomplete.css"
import MoAddressSearchTemplate from "./MoAddressSearchTemplate.vue"
import { MoInputAutocomplete } from "@/components/MoInput"
import MoInputBase from "@/components/MoInput/MoInputBase"

export default {
  extends: MoInputBase,
  name: "MoAddressSearchField",

  components: {
    MoInputAutocomplete,
  },

  props: {
    /**
     * Enable global search
     * @default false
     * @type {Boolean}
     */
    global: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      /**
       * Results from query
       * @type {Array}
       */
      addressSuggestions: [],

      /**
       * Results template
       */
      template: MoAddressSearchTemplate,
    }
  },
  methods: {
    /**
     * Get a label to display
     * @returns {String}
     */
    getLabel(item) {
      return item ? item.location.name : ""
    },

    /**
     * Update address suggestions based on search query.
     */
    getGeographicalLocation(query) {
      let vm = this
      let org = this.$store.state.organisation
      if (org.uuid === undefined) return
      Search.getGeographicalLocation(org.uuid, query, this.global).then((response) => {
        vm.addressSuggestions = response
      })
    },
  },
}
</script>
