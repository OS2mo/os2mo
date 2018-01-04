<template>
    <select 
      class="form-control" 
      id="organisation-picker"
      v-model="selectedOrganisation"
      @change="updateOrganisation()"
    >
      <option disabled selected>Vælg organisation</option>
      <option 
        v-for="org in orgs" 
        :key="org.uuid"
        :value="org">
        {{org.name}}
      </option>
    </select>
</template>

<script>
import Organisation from '../api/Organisation'

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
    this.selectedOrganisation = Organisation.getSelectedOrganisation()
  },
  methods: {
    getAll () {
      var vm = this
      Organisation.getAll()
      .then(response => {
        vm.orgs = response
      })
    },

    updateOrganisation () {
      Organisation.setSelectedOrganisation(this.selectedOrganisation)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>