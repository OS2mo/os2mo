<template>
  <div class="card">
    <div class="card-body">
      <loading v-show="isLoading"/>
      <div v-show="!isLoading">
      <h4 class="card-title">{{org.name}}</h4>
      <div class="row justify-content-md-center">
        <info-box icon="user" label="Medarbejdere" :info="org.person_count"/>
        <info-box icon="globe" label="Org funker" :info="org.employment_count"/>
        <info-box icon="users" label="Enheder" :info="org.unit_count"/>
      </div>
      </div>
    </div>
</div>

</template>

<script>
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
  import InfoBox from '../components/InfoBox'
  import Loading from '../components/Loading'
  
  export default {
    components: {
      InfoBox,
      Loading
    },
    data () {
      return {
        org: {},
        isLoading: false
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
        vm.isLoading = true
        Organisation.get(newOrg.uuid)
        .then(response => {
          vm.org = response
          vm.isLoading = false
        })
      }
    }
  }
</script>
