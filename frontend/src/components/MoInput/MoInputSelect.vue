SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group">
    <label v-if="hasLabel" :for="identifier">{{ label }}</label>
    <select
      v-if="hasOptions"
      class="form-control"
      :name="identifier"
      :id="identifier"
      :ref="identifier"
      :data-vv-as="label"
      v-model="internalValue"
      :disabled="disabled"
      v-validate="{ required: isRequired }"
    >
      <option disabled selected>{{ label }}</option>
      <option v-for="(o, index) in options" :key="index" :value="o">
        {{ display_method(o) }}
      </option>
    </select>

    <span v-show="errors.has(identifier)" class="text-danger">
      {{ errors.first(identifier) }}
    </span>
  </div>
</template>

<script>
/**
 * Select component.
 */
import MoInputBase from "./MoInputBase"
export default {
  extends: MoInputBase,
  name: "MoInputSelect",

  props: {
    /**
     * List of all options.
     * @type {Array}
     */
    options: {
      type: Array,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    display_method: {
      type: Function,
      default: (value) => value.name,
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
  computed: {
    /**
     * Are there any options
     * @type {Boolean}
     */
    hasOptions() {
      return this.options.length > 0
    },
  },
}
</script>
