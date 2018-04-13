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

export default {
  name: 'MoInput',
  inject: {
    $validator: '$validator'
  },
  props: {
    value: String,
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
      return 'mo-input-' + this._uid
    }
  },
  watch: {
    selected (val) {
      this.$emit('input', val)
    }
  },
  created () {
    this.selected = this.value
  }
}
</script>
