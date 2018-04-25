<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>
      <div v-if="!isLoading">
        <h4 class="card-title">{{org.name}}</h4>
        <div class="row justify-content-md-center">
          <info-box icon="user" :label="$tc('shared.employee', 2)" :info="info.person_count"/>
          <info-box icon="globe" label="Org funker" :info="info.employment_count"/>
          <info-box icon="users" :label="$tc('shared.unit', 2)" :info="info.unit_count"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Organisation from '@/api/Organisation'
import InfoBox from '@/components/InfoBox'
import MoLoader from '@/components/atoms/MoLoader'
import { mapGetters } from 'vuex'

export default {
  components: {
    InfoBox,
    MoLoader
  },
  data () {
    return {
      info: {},
      isLoading: false
    }
  },
  computed: {
    ...mapGetters({
      org: 'organisation/get'
    })
  },
  watch: {
    org: {
      handler () {
        this.getOrganisationDetails()
      },
      deep: true
    }
  },
  mounted () {
    this.$store.commit('organisationUnit/reset')
    this.getOrganisationDetails()
  },
  methods: {
    getOrganisationDetails () {
      if (this.org.uuid == null) return
      let vm = this
      vm.isLoading = true
      Organisation.get(this.org.uuid)
        .then(response => {
          vm.info = response
          vm.isLoading = false
        })
    }
  }
}
</script>
