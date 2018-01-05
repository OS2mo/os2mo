<template>
    <select 
      class="form-control" 
      id="organisation-picker"
      v-model="selectedOrganisation"
      @change="updateOrganisation()"
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
      var vm = this
      Organisation.getAll()
      .then(response => {
        vm.orgs = response
      })
    },

    getSelectedOrganisation () {
      this.selectedOrganisation = Organisation.getSelectedOrganisation()
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