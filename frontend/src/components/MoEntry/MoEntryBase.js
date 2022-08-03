// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"

export default Vue.extend({
  name: "MoEntryBase",

  props: {
    /**
     * Create two-way data bindings with the component.
     * @default null,
     * @type {Object}
     */
    value: {
      type: Object,
      default: null,
    },

    /**
     * This boolean property hides the validity.
     * @default false,
     * @type {Boolean}
     */
    validityHidden: {
      type: Boolean,
      default: false,
    },
    /**
     * The valid dates for the entry component date pickers.
     * @default null
     * @type {Object}
     */
    disabledDates: Object,

    /**
     * Whether we are using the entry for editing the entry
     * true if editing, false if creating
     */
    isEdit: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      /**
       * The entry component value.
       * @default {}
       * @type {Object}
       */
      entry: {},
    }
  },
  computed: {
    /**
     * unique name.
     * @default mo-entry-<uid>
     * @type {String}
     */
    identifier() {
      return "mo-entry-" + this._uid
    },
  },
  created() {
    /**
     * Called synchronously after the instance is created.
     * Set entry to value.
     */
    this.entry = this.value
  },
})
