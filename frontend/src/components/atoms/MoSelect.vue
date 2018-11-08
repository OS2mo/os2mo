<template>
  <div class="form-group col">
    <label :for="nameId">{{label}}</label>
    
    <select 
      :name="nameId"
      :id="nameId"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      :disabled="disabled"
      @change="$emit('input', selected)"
      v-validate="{ required: isRequired }"
    >
      <option disabled>{{label}}</option>
      <option v-for="o in options" :key="o.uuid" :value="o">
          {{o.name}}
      </option>
    </select>
    
    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
  /**
   * A select component.
   */
  export default {
    name: 'MoSelect',

      /**
       * Validator scope, sharing all errors and validation state.
       */
    inject: {
      $validator: '$validator'
    },

    props: {
      /**
       * @model
       */
      value: Object,

      /**
       * Defines options value.
       */
      options: Array,

      /**
       * Defines the label.
       */
      label: String,

      /**
       * This boolean property requires a selected name.
       */
      required: Boolean,

      /**
       * This boolean property disable the label.
       */
      disabled: Boolean
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
       * Get name `mo-select`.
       */
      nameId () {
        return 'mo-select-' + this._uid
      },
  
      /**
       * If its not disable, change it to required.
       */
      isRequired () {
        if (this.disabled) return false
        return this.required
      }
    },

    watch: {
      /**
       * Whenever value change, set selected to the new val and validate the name.
       */
      value (val) {
        this.selected = val
        this.$validator.validate(this.nameId)
      }
    }
  }
</script>
