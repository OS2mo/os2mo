SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group col">
    <label v-if="hasLabel" :for="identifier">{{ label }}</label>

    <v-autocomplete
      v-model="internalValue"
      :items="items"
      :name="identifier"
      :data-vv-as="label"
      :get-label="getLabel"
      :component-item="componentItem"
      @update-items="updateItems"
      :min-len="minLen"
      v-validate="{ required: isRequired }"
    />

    <span v-show="errors.has(identifier)" class="text-danger">
      {{ errors.first(identifier) }}
    </span>
  </div>
</template>

<script>
/**
 * Autocomplete component
 */
import MoInputBase from "./MoInputBase"
import VAutocomplete from "v-autocomplete"
import "v-autocomplete/dist/v-autocomplete.css"

export default {
  /**
   * This component is a little different, because it is an extention of two components.
   * But I couldn't figure out how to extend from two different sources, but it made it
   * work by extending from one and mixing in the other.
   */
  extends: VAutocomplete,
  mixins: [MoInputBase],
  name: "MoInputAutocomplete",
  components: {
    /* TODO: Use `MoAutocomplete` instead which relies on a better third party
     * autocomplete widget. */
    VAutocomplete,
  },
  methods: {
    updateItems(query) {
      this.$emit("update-items", query)
    },
  },
}
</script>
