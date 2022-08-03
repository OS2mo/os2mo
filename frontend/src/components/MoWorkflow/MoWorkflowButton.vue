SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <button type="button" class="btn btn-primary btn-workflow">
    <icon class="btn-icon" :name="icon" />
    <label class="btn-label">{{ label }}</label>
  </button>
</template>

<script>
/**
 * A workflow button component.
 */

export default {
  name: "MoWorkflowButton",

  props: {
    /**
     * Defines a required label.
     */
    label: { type: String, required: true },

    /**
     * Defines a required icon.
     */
    icon: { type: String, required: true },
  },
}
</script>

<style lang="scss" scoped>
.btn-workflow {
  display: block;
  height: 38px;
  margin-bottom: 4px;
  text-align: left;
  width: 300px;
  position: relative;
  right: 0;
  transition: right 0.15s;
  transition-delay: 0.05s;
  transition-timing-function: ease-in;

  &:hover {
    right: 235px;
    transition: right 0.25s;
    transition-timing-function: ease-out;
  }

  .btn-label {
    padding-left: 25px;
    position: absolute;
  }

  .btn-icon {
    width: 24px;
    height: 24px;
  }
}
</style>
