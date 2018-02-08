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

export default {
  name: 'JobFunctionPicker',
  props: {
    value: Object,
    noLabel: Boolean,
    org: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      label: 'Stillingsbetegnelse',
      selected: {},
      jobFunctions: []
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
      Facet.jobFunctions(this.org.uuid)
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