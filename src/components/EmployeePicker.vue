<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <loading v-show="isLoading"/>
    <select
      v-show="!isLoading" 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedEmployee()">
      <option disabled>{{label}}</option>
      <option 
        v-for="e in employees" 
        v-bind:key="e.uuid"
        :value="e">
          {{e.name}}
      </option>
    </select>
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
    value: Object
  },
  data () {
    return {
      label: 'Medarbejder',
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
