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

export default {
  name: 'RolePicker',
  props: {
    value: Object,
    orgUuid: String
  },
  data () {
    return {
      selected: {},
      roleTypes: []
    }
  },
  watch: {
    orgUuid () {
      this.getRoleTypes()
    }
  },
  methods: {
    getRoleTypes () {
      var vm = this
      Facet.roleTypes(this.orgUuid)
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