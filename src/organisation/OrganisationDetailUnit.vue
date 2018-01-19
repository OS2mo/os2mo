<template>
  <div>
    <mo-table 
      title="Fremtiden"
      :labels="labels" 
      :content="detailsFuture"
      @click.native="getDetailsFuture()"
    />
    <mo-table 
      title="Nutidig"
      :labels="labels" 
      :content="details"
      visible
      @click.native="getDetailsPast()"
    />
    <mo-table 
      title="Fortid"
      :labels="labels" 
      :content="detailsPast"
      @click.native="getDetailsPast()"
    />
  </div>
</template>


<script>
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
  import MoTable from '../components/MoTable'

  export default {
    components: {
      MoTable
    },
    data () {
      return {
        details: [],
        detailsPast: [],
        detailsFuture: [],
        labels: ['Enhedsnavn', 'Enhedstype', 'Overenhed', 'Startdato', 'Slutdato']
      }
    },
    created () {
      this.getDetails()
    },
    mounted () {
      EventBus.$on('org-unit-rename', () => {
        this.getDetails()
      })
    },
    methods: {
      getDetails () {
        let vm = this
        Organisation.getUnitDetails(this.$route.params.uuid)
        .then(response => {
          vm.details = response
        })
      },

      getDetailsPast () {
        let vm = this
        Organisation.getUnitDetails(this.$route.params.uuid, 'past')
        .then(response => {
          vm.detailsPast = response
        })
      },

      getDetailsFuture () {
        let vm = this
        Organisation.getUnitDetails(this.$route.params.uuid, 'future')
        .then(response => {
          vm.detailsFuture = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
