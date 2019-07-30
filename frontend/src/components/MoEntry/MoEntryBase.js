import Vue from 'vue'

export default Vue.extend({
  name: 'MoEntryBase',

  props: {
    /**
     * Create two-way data bindings with the component.
     * @default null,
     * @type {Object}
     */
    value: {
      type: Object,
      default: null
    },

    /**
     * This boolean property hides the validity.
     * @default false,
     * @type {Boolean}
     */
    validityHidden: {
      type: Boolean,
      default: false
    },
    /**
     * The valid dates for the entry component date pickers.
     * @default null
     * @type {Object}
     */
    disabledDates: Object
  },

  data () {
    return {
      /**
      * The entry component value.
      * @default {}
      * @type {Object}
      */
      entry: {}
    }
  },
  computed: {
    /**
     * unique name.
     * @default mo-entry-<uid>
     * @type {String}
     */
    identifier () {
      return 'mo-entry-' + this._uid
    }
  },
  created () {
    /**
     * Called synchronously after the instance is created.
     * Set entry to value.
     */
    this.entry = this.value
    this.entry.org = this.$store.getters['organisation/GET_ORGANISATION']
  }
})
