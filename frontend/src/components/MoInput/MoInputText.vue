SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group col">
    <label v-if="hasLabel" :for="identifier">{{ label }}</label>

    <input
      class="form-control"
      type="text"
      :placeholder="placeholder"
      :name="identifier"
      :id="identifier"
      :ref="identifier"
      :data-vv-as="label"
      v-model="internalValue"
      :disabled="disabled"
      v-validate="{ required: isRequired }"
    />

    <span v-show="errors.has(identifier)" class="text-danger">
      {{ errors.first(identifier) }}
    </span>
  </div>
</template>

<script>
/**
 * Text input component
 */
import MoInputBase from "./MoInputBase"

export default {
  extends: MoInputBase,
  name: "MoInputText",

  props: {
    /**
     * Set a placeholder value.
     * @default null
     * @type {String}
     */
    placeholder: {
      type: String,
      default: null,
    },
  },
}
</script>
