<template>
  <div class="form-group col">
    <label v-if="!noLabel">{{label}}</label>
    <select 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedJobFunction()">
      <option disabled>{{label}}</option>
      <option 
        v-for="jf in jobFunctions" 
        v-bind:key="jf.uuid"
        :value="jf">
          {{jf.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'JobFunctionPicker',
  props: {
    value: Object,
    noLabel: Boolean
  },
  data () {
    return {
      label: 'Stillingsbetegnelse',
      selected: {},
      jobFunctions: []
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getJobFunctions()
    })
  },
  created () {
    this.getJobFunctions()
    this.selected = this.value
  },
  methods: {
    getJobFunctions () {
      var vm = this
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Facet.jobFunctions(org.uuid)
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
