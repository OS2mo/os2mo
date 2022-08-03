SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <label class="container mb-3 mt-2"
      >{{ $t("input_fields.primary") }}
      <input
        type="checkbox"
        v-model="internalValue"
        :data-vv-as="label"
        :name="identifier"
        :id="identifier"
        :ref="identifier"
        v-validate="{ required: isRequired }"
      />
      <span class="checkmark"></span>
    </label>

    <span v-show="errors.has(identifier)" class="text-danger">
      {{ errors.first(identifier) }}
    </span>
  </div>
</template>

<script>
/**
 * Checkbox input component.
 */
import MoInputBase from "./MoInputBase"

export default {
  extends: MoInputBase,
  name: "MoInputCheckbox",
}
</script>

<style scoped>
.container {
  width: 110px;
  position: relative;
  padding-left: 35px;
  margin-bottom: 12px;
  cursor: pointer;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* Hide the browser's default checkbox */
.container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

/* Create a custom checkbox */
.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 22px;
  width: 22px;
  background-color: #ced4da;
}

/* When the checkbox is checked, add a blue background */
.container input:checked ~ .checkmark {
  background-color: #007bff;
}

/* Create the checkmark/indicator (hidden when not checked) */
.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

/* Show the checkmark when checked */
.container input:checked ~ .checkmark:after {
  display: block;
}

/* Style the checkmark/indicator */
.container .checkmark:after {
  left: 9px;
  top: 5px;
  width: 5px;
  height: 10px;
  border: solid #ffffff;
  border-width: 0 3px 3px 0;
  -webkit-transform: rotate(45deg);
  -ms-transform: rotate(45deg);
  transform: rotate(45deg);
}
</style>
