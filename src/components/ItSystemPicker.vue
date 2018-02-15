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
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'ItSystemPicker',
  props: {
    value: Object
  },
  data () {
    return {
      label: 'IT systemer',
      selected: {},
      itSystems: []
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getItSystems()
    })
  },
  created () {
    this.selected = this.value
    this.getItSystems()
  },
  methods: {
    getItSystems () {
      var vm = this
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Facet.itSystems(org.uuid)
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