<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select 
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

export default {
  name: 'EmployeePicker',
  props: {
    value: Object,
    preselected: Object,
    org: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      label: 'Medarbejder',
      selected: {},
      employees: []
    }
  },
  watch: {
    org () {
      this.getJobFunctions()
    }
  },
  methods: {
    getJobFunctions () {
      var vm = this
      Search.employees(this.org.uuid)
      .then(response => {
        vm.employees = response
      })
    },

    updateSelectedEmployee () {
      this.$emit('input', this.selected)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>