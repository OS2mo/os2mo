<template>
  <div>
    <label v-if="!noLabel">{{label}}</label>
    <!-- <loading v-show="isLoading"/> -->
    <v-autocomplete
      name="employee-picker"
      :data-vv-as="label"
      :items="items" 
      v-model="item" 
      :get-label="getLabel" 
      :component-item="template" 
      @item-selected="selected"
      @update-items="updateItems"
      :auto-select-one-item="false"
      :min-len="2"
      placeholder="Søg efter medarbejder"
      v-validate="{ required: required }"
    />
    <span
      v-show="errors.has('employee-picker')" 
      class="text-danger"
    >
      {{ errors.first('employee-picker') }}
    </span>
  </div>
</template>

<script>
import Search from '../api/Search'
import VAutocomplete from 'v-autocomplete'
import 'v-autocomplete/dist/v-autocomplete.css'
import TheSearchBarTemplate from './TheSearchBarTemplate.vue'

export default {
  name: 'EmployeePicker',
  components: {
    VAutocomplete
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    noLabel: Boolean,
    label: {
      type: String,
      default: 'Medarbejder'
    },
    required: Boolean
  },
  data () {
    return {
      item: null,
      items: [],
      template: TheSearchBarTemplate
    }
  },
  methods: {
    getLabel (item) {
      return item ? item.name : null
    },

    updateItems (query) {
      let vm = this
      vm.items = []
      let org = this.$store.state.organisation
      Search.employees(org.uuid, query)
        .then(response => {
          vm.items = response
        })
    },

    selected (value) {
      this.$emit('input', value)
    }
  }
}
</script>
