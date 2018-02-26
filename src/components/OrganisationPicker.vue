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
    value: Object,
    atDate: Date,
    resetRoute: Boolean
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
      if (this.resetRoute) {
        this.resetToBaseRoute()
      }
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
    },

    // resets the route back to base. So if we're viewing an employee, it goes back to the employee list
    resetToBaseRoute () {
      if (this.$route.name.indexOf('Organisation') > -1) {
        this.$router.push({name: 'Organisation'})
      }
      if (this.$route.name.indexOf('Employee') > -1) {
        this.$router.push({name: 'Employee'})
      }
    }
  }
}
</script>
