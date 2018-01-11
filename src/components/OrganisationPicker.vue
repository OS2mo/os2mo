<template>
    <select 
      class="form-control" 
      id="organisation-picker"
      v-model="selectedOrganisation"
      @change="setSelectedOrganisation(selectedOrganisation)"
    >
      <option disabled>Vælg organisation</option>
      <option 
        v-for="org in orgs" 
        :key="org.uuid"
        :value="org"
      >
        {{org.name}}
      </option>
    </select>
</template>

<script>
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'OrganisationPicker',
  data () {
    return {
      selectedOrganisation: null,
      orgs: []
    }
  },
  created () {
    this.getAll()
    this.getSelectedOrganisation()
  },
  mounted () {
    EventBus.$on('organisation-changed', newOrg => {
      this.selectedOrganisation = newOrg
    })
  },
  methods: {

    getAll () {
      let vm = this
      return Organisation.getAll()
      .then(response => {
        vm.orgs = response
        vm.selectedOrganisation = response[0]
        EventBus.$emit('organisation-changed', response[0])
      })
    },

    getSelectedOrganisation () {
      this.selectedOrganisation = Organisation.getSelectedOrganisation()
    },

    setSelectedOrganisation (selOrg) {
      Organisation.setSelectedOrganisation(selOrg)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>