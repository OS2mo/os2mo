<template>
  <b-modal 
    id="orgUnitTerminate"
    ref="orgUnitTerminate"  
    size="lg" 
    hide-footer 
    title="Afslut enhed"
    lazy
  >
    <div class="form-row">
      <organisation-unit-picker 
        label="Enhed" 
        class="col"
        v-model="org_unit"
      />
      <date-picker 
        label="Slutdato"
        v-model="terminate.validity.from"
      />
    </div>
    <div class="float-right">
      <button-submit
      :is-disabled="isDisabled"
      :on-click-action="endOrganisationUnit"
      />
    </div>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import DatePicker from '../components/DatePicker'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DatePicker,
      OrganisationUnitPicker,
      ButtonSubmit
    },
    computed: {
      isDisabled () {
        if (this.org_unit.uuid === undefined || this.terminate.validity.from === undefined) return true
      }
    },
    data () {
      return {
        org_unit: {},
        terminate: {
          validity: {}
        }
      }
    },
    mounted () {
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
      endOrganisationUnit () {
        let vm = this
        OrganisationUnit.terminate(this.org_unit.uuid, this.terminate)
        .then(response => {
          vm.$refs.orgUnitTerminate.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>