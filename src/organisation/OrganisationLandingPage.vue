<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">{{org.name}}</h4>
      
      <p>Medarbejdere: {{org.person_count}}</p>
      <p>Org funker: {{org.employment_count}}</p>
      <p>Enheder: {{org.unit_count}}</p>
    </div>
  </div>
</template>


<script>
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
  export default {
    components: {},
    data () {
      return {
        org: {}
      }
    },
    created () {
      this.getOrganisationDetails(Organisation.getSelectedOrganisation())
    },
    mounted () {
      EventBus.$on('organisation-changed', newOrg => {
        this.getOrganisationDetails(newOrg)
      })
    },
    methods: {
      getOrganisationDetails (newOrg) {
        let vm = this
        Organisation.get(newOrg.uuid)
        .then(response => {
          vm.org = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>