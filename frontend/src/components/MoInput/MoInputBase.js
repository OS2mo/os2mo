import Vue from 'vue'

export default Vue.extend({
  name: 'MoInputBase',

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
     * @model
     * @type {String||Object||Array||Integer}
     */
    value: null,
    /**
     * Set the id.
     * @default null
     * @type {String||Integer}
     */
    id: {
      type: [String, Number],
      default: null
    },
    /**
     * Set a label.
     * @default null
     * @type {String}
     */
    label: {
      type: String,
      default: null
    },
    /**
     * Wether this field is required.
     * @default false
     * @type {Boolean}
     */
    required: {
      type: Boolean,
      default: false
    },
    /**
     * Wether this field is disabled.
     * @default false
     * @type {Boolean}
     */
    disabled: {
      type: Boolean,
      default: false
    }
  },

  data () {
    return {
      internalValue: null
    }
  },

  computed: {
    identifier () {
      return this.id ? this.id : 'mo-input-' + this._uid
    },

    hasLabel () {
      return this.label != null
    },

    isRequired () {
      return this.disabled ? false : this.required
    }
  },

  methods: {
    update (event) {
      this.$emit('input', event.target.value)
    }
  }
})
