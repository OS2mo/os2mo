<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedItSystem()">
      <option disabled>{{label}}</option>
      <option 
        v-for="it in itSystems" 
        v-bind:key="it.uuid"
        :value="it">
          {{it.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Facet from '../api/Facet'

export default {
  name: 'ItSystemPicker',
  props: {
    value: Object,
    orgUuid: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      label: 'IT systemer',
      selected: {},
      itSystems: []
    }
  },
  watch: {
    orgUuid () {
      this.getItSystems()
    }
  },
  methods: {
    getItSystems () {
      var vm = this
      Facet.itSystems(this.orgUuid)
      .then(response => {
        vm.itSystems = response
      })
    },

    updateSelectedItSystem () {
      this.$emit('input', this.selected)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>