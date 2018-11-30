<template>
  <div class="form-group col">
    <label for="">{{label}}</label>

    <input
      v-model="selected"
      :name="nameId"
      :data-vv-as="label"
      type="text"
      class="form-control"
      v-validate="{required: required}"
    >

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
/**
 * A input component.
 */

export default {
  name: 'MoInput',

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: String,

    /**
     * Defines the label.
     */
    label: String,

    /**
     * This boolean property requries input data.
     */
    required: Boolean
  },

  data () {
    return {
      /**
       * The selected component value.
       * Used to detect changes and restore the value.
       */
      selected: null
    }
  },

  computed: {
    /**
     * Get name `mo-input`.
     */
    nameId () {
      return 'mo-input-' + this._uid
    }
  },

  watch: {
    /**
     * Whenever selected change update val.
     */
    selected (val) {
      this.$emit('input', val)
    }
  },

  created () {
    /**
     * Called synchronously after the instance is created.
     * Set selected to value.
     */
    this.selected = this.value
  }
}
</script>
