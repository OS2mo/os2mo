// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"

export default Vue.extend({
  name: "MoInputBase",

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  props: {
    /**
     * @model
     * @type {String||Object||Array||Integer||Date}}
     */
    value: null,
    /**
     * Set the id.
     * @default null
     * @type {String||Integer}
     */
    id: {
      type: [String, Number],
      default: null,
    },
    /**
     * Set a label.
     * @default null
     * @type {String}
     */
    label: {
      type: String,
      default: null,
    },
    /**
     * Wether this field is required.
     * @default false
     * @type {Boolean}
     */
    required: {
      type: Boolean,
      default: false,
    },
    /**
     * Wether this field is disabled.
     * @default false
     * @type {Boolean}
     */
    disabled: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      internalValue: null,
    }
  },

  computed: {
    /**
     * Provide a unique identifier
     * @type {String}
     */
    identifier() {
      return this.id ? this.id : "mo-input-" + this._uid
    },

    /**
     * Does it have a label
     * @type {Boolean}
     */
    hasLabel() {
      return this.label != null
    },

    /**
     * Is the field required
     * @type {Boolean}
     */
    isRequired() {
      return this.disabled ? false : this.required
    },
  },
  watch: {
    /**
     * Emit internal value when it changes
     * @emits value
     */
    internalValue(newVal) {
      this.$emit("input", newVal)
    },

    /**
     * Whenever value change, set selected to the new val and validate the name.
     */
    value(val) {
      this.internalValue = val
      if (document.getElementById(this.identifier)) {
        this.$validator.validate(this.identifier)
      }
    },
  },
  created() {
    this.internalValue = this.value
  },
})
