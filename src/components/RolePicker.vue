<template>
  <div class="form-group col">
    <label>Rolle</label>
    <select 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedRoleTypes()">
      <option disabled>Rolle</option>
      <option 
        v-for="rt in roleTypes" 
        v-bind:key="rt.uuid"
        :value="rt">
          {{rt.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'RolePicker',
  props: {
    value: Object,
    noLabel: Boolean
  },
  data () {
    return {
      selected: {},
      roleTypes: []
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getRoleTypes()
    })
  },
  created () {
    this.getRoleTypes()
  },
  methods: {
    getRoleTypes () {
      var vm = this
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Facet.roleTypes(org.uuid)
      .then(response => {
        vm.roleTypes = response
      })
    },

    updateSelectedRoleTypes () {
      this.$emit('input', this.selected)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>