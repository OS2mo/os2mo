<template>
  <div>
    <select 
      class="form-control" 
      id="organisation-picker"
      v-model="selectedOrganisation"
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
  </div>
</template>

<script>
import Organisation from '../api/Organisation'

export default {
  name: 'OrganisationPicker',
  props: {
    value: null,
    atDate: Date
  },
  data () {
    return {
      selectedOrganisation: null,
      orgs: []
    }
  },
  created () {
    this.getAll()
  },
  watch: {
    selectedOrganisation (newVal) {
      Organisation.setSelectedOrganisation(newVal)
      this.$emit('input', newVal)
    },

    atDate () {
      this.getAll()
    }
  },
  methods: {
    getAll () {
      let vm = this
      Organisation.getAll(this.atDate)
      .then(response => {
        vm.orgs = response
        vm.selectedOrganisation = response[0]
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>