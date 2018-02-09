<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">{{org.name}}</h4>
      <div class="row justify-content-md-center">
        <div class="col-sm-3 box text-white">
          <icon name="user" scale="3"/>
          <p>Medarbejdere</p>
          <span class="text-size">{{org.person_count}}</span>
        </div>
        <div class="col-sm-3 box text-white ml-3">
          <icon name="globe" scale="3"/>
          <p>Org funker</p>
          <span class="text-size">{{org.employment_count}}</span>
        </div>
        <div class="col-sm-3 box text-white ml-3">
          <icon name="users" scale="3"/>
          <p>Enheder</p>
          <span class="text-size">{{org.unit_count}}</span>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'

  export default {
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

  .box{
    background-color: #007bff;
    min-height: 10vh;
    display: block;
    text-align: center;
    padding-top: 1vh;
  }

  .text-size{
    line-height: 0vh;
    font-size: 2vh;
  }
</style>