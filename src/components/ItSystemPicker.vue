<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select 
      name="it-system-picker"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedItSystem()"
      v-validate="{ required: true }">
      <option disabled>{{label}}</option>
      <option 
        v-for="it in itSystems" 
        v-bind:key="it.uuid"
        :value="it.uuid">
          {{it.name}}
      </option>
    </select>
    <span
      v-show="errors.has('it-system-picker')" 
      class="text-danger"
    >
      {{ errors.first('it-system-picker') }}
    </span>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'ItSystemPicker',
  props: {
    value: Object,
    preselected: String
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
    this.selected = this.preselected
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
      let data = {
        uuid: this.selected
      }
      this.$emit('input', data)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>