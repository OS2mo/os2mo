<template>
  <div>
    <label v-if="!noLabel">{{label}}</label>
    <loading v-show="isLoading"/>
    <select
      v-show="!isLoading" 
      name="employee-picker"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedEmployee()"
      v-validate="{ required: true }"
    >
      <option disabled>{{label}}</option>
      <option 
        v-for="e in employees" 
        v-bind:key="e.uuid"
        :value="e">
          {{e.name}}
      </option>
    </select>
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
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'
import Loading from './Loading'

export default {
  name: 'EmployeePicker',
  components: {
    Loading
  },
  props: {
    value: Object,
    noLabel: Boolean,
    label: {
      type: String,
      default: 'Medarbejder'
    }
  },
  data () {
    return {
      selected: {},
      employees: [],
      isLoading: false
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getEmployees()
    })
  },
  created () {
    this.getEmployees()
    this.selected = this.value
  },
  methods: {
    getEmployees () {
      var vm = this
      vm.isLoading = true
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Search.employees(org.uuid)
        .then(response => {
          vm.isLoading = false
          vm.employees = response
        })
    },

    updateSelectedEmployee () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
