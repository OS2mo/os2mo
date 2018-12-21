<template>
  <div class="form-group col">
    <label v-if="hasLabel" :for="identifier">{{label}}</label>
    <select
      v-if="hasOptions"
      class="form-control col"
      :name="identifier"
      :id="identifier"
      :ref="identifier"
      :data-vv-as="label"
      v-model="internalValue"
      :disabled="disabled"
      @change="$emit('input', internalValue)"
      v-validate="{ required: isRequired }"
    >
      <option disabled selected>{{label}}</option>
      <option v-for="(o, index) in options" :key="index" :value="o">
          {{o.name}}
      </option>
    </select>

    <span v-show="errors.has(identifier)" class="text-danger">
      {{ errors.first(identifier) }}
    </span>
  </div>
</template>

<script>
/**
 * A select component.
 */
import MoInputBase from './MoInputBase'
export default {
  extends: MoInputBase,
  name: 'MoInputSelect',

  props: {
    /**
     * List of all options.
     * @type {Array}
     */
    options: {
      type: Array,
      required: true
    }
  },

  computed: {
    hasOptions () {
      return this.options.length > 0
    }
  },

  watch: {
    /**
     * Whenever value change, set selected to the new val and validate the name.
     */
    value (val) {
      this.internalValue = val
      this.$validator.validate(this.identifier)
    }
  }
}
</script>
