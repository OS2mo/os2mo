<template>
  <div class="card">
    <div class="card-body">
      <loading v-show="isLoading"/>
      <div v-if="!isLoading">
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
    mounted () {
      this.getOrganisationDetails()
      EventBus.$on('organisation-changed', () => {
        this.getOrganisationDetails()
      })
    },
    beforeDestroy () {
      EventBus.$off(['organisation-changed'])
    },
    methods: {
      getOrganisationDetails () {
        let vm = this
        vm.isLoading = true
        let org = this.$store.state.organisation
        if (org.uuid === undefined) return
        Organisation.get(org.uuid)
          .then(response => {
            vm.org = response
            vm.isLoading = false
          })
      }
    }
  }
</script>
