SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div
    class="input-group alert"
    :class="errors.has(identifier) ? 'alert-warning' : 'alert-success'"
    v-show="showAlert"
  >
    <input
      v-model="cprApproved"
      data-vv-as="checkbox"
      :name="identifier"
      type="checkbox"
      v-validate="'required'"
    />
    <h5>{{ value.name }}</h5>
  </div>
</template>

<script>
/**
 * A cpr result component.
 */

export default {
  name: "MoCprResult",

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,
  },

  data() {
    return {
      /**
       * The cprApproved component value.
       * Used to detect changes and restore the value.
       */
      cprApproved: false,
    }
  },

  mounted() {
    this.$validator.validate(this.identifier)
  },

  computed: {
    /**
     * Get name `cpr-result`.
     */
    identifier() {
      return "cpr-result"
    },

    /**
     * Show cpr alert.
     */
    showAlert() {
      return Object.keys(this.value).length > 0
    },
  },

  watch: {
    /**
     * Whenever value change, validate name and cpr alert.
     */
    value() {
      this.cprApproved = false
      this.$validator.validate(this.identifier)
    },
  },
}
</script>
