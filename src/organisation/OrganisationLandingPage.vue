<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>
      <div v-if="!isLoading">
        <h4 class="card-title">{{org.name}}</h4>
        <div class="row justify-content-md-center">
          <info-box icon="user" :label="$tc('shared.employee', 2)" :info="org.person_count"/>
          <info-box icon="globe" label="Org funker" :info="org.employment_count"/>
          <info-box icon="users" :label="$tc('shared.unit', 2)" :info="org.unit_count"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Organisation from '@/api/Organisation'
import { EventBus } from '@/EventBus'
import InfoBox from '@/components/InfoBox'
import MoLoader from '@/components/atoms/MoLoader'

export default {
  components: {
    InfoBox,
    MoLoader
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
