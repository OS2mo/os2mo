<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">{{org.name}}</h4>
      <p>Jeg er en landingpage for en organisation</p>
      <p>Vi kunne have noget sweet indhold her, som fx. statistik om antal enheder, brugere, eller noget andet spændende.</p>
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
      this.getOrganisation()
    },
    mounted () {
      EventBus.$on('organisation-changed', newOrg => {
        this.org = newOrg
      })
    },
    methods: {
      getOrganisation () {
        let vm = this
        Organisation.getSelectedOrganisation()
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