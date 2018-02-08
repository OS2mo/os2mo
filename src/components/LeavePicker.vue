<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedJobFunction()">
      <option disabled>{{label}}</option>
      <option 
        v-for="lt in leaveTypes" 
        v-bind:key="lt.uuid"
        :value="lt">
          {{lt.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Facet from '../api/Facet'

export default {
  name: 'LeavePicker',
  props: {
    value: Object,
    orgUuid: String
  },
  data () {
    return {
      label: 'Orlovstype',
      selected: {},
      leaveTypes: []
    }
  },
  watch: {
    orgUuid () {
      this.getJobFunctions()
    }
  },
  methods: {
    getJobFunctions () {
      var vm = this
      Facet.jobFunctions(this.orgUuid)
      .then(response => {
        vm.jobFunctions = response
      })
    },

    updateSelectedJobFunction () {
      this.$emit('input', this.selected)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>