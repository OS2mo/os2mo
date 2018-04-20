<template>
  <div class="form-group col">
    <label :for="nameId">{{label}}</label>
    <select 
      :name="nameId"
      :id="nameId"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="$emit('input', selected)"
      v-validate="{ required: required }"
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
export default {
  name: 'MoSelect',
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    options: Array,
    label: String,
    required: Boolean
  },
  data () {
    return {
      selected: null
    }
  },
  computed: {
    nameId () {
      return 'mo-select-' + this._uid
    }
  },
  watch: {
    value (val) {
      this.selected = val
      this.$validator.validate(this.nameId)
    }
  }
}
</script>
