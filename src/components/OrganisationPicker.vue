<template>
    <select 
      class="form-control" 
      id="organisation-picker"
      v-model="selectedOrganisation"
      @change="setSelectedOrganisation()"
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

/**
 * The Organisation picker component
 * @author Anders Jepsen
 * @input
 */

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
    /**
     * Fired when organisation is changed
     */
    EventBus.$on('organisation-changed', newOrg => {
      this.selectedOrganisation = newOrg
    })
  },
  methods: {

    /**
     * Get all organisations
     */
    getAll () {
      let vm = this
      return Organisation.getAll()
      .then(response => {
        vm.orgs = response
      })
    },

    /**
     * Get selected organisation
     */
    getSelectedOrganisation () {
      this.selectedOrganisation = Organisation.getSelectedOrganisation()
    },

    /**
     * Set selected organisation
     */
    setSelectedOrganisation () {
      Organisation.setSelectedOrganisation(this.selectedOrganisation)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>