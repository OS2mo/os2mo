<template>
  <div class="form-group col">
    <label>Stillingsbetegnelse</label>
    <select 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedJobFunction()">
      <option disabled>Stillingsbetegnelse</option>
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
    value: String
  },
  data () {
    return {
      selected: {},
      jobFunctions: []
    }
  },
  created () {
    this.getJobFunctions()
  },
  methods: {
    getJobFunctions () {
      var vm = this
      Facet.jobFunctions()
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