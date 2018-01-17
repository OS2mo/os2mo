<template>
  <b-modal 
    id="orgUnitEnd"
    ref="orgUnitEnd"  
    size="lg" 
    hide-footer 
    title="Afslut enhed">
    <div class="form-row">
      <organisation-unit-picker 
        label="Enhed" 
        class="col"
        v-model="orgUnit"
        :preselected="preselectedUnit"
      />
      <date-picker 
        label="Slutdato"
        v-model="endDate"
      />
    </div>
    <div class="float-right">
      <button-submit 
      :disabled="errors.any() || !isCompleted" 
      @click.native="endOrganisationUnit"
      />
    </div>
  </b-modal>
</template>

<script>
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
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
      isCompleted () {
        return this.orgUnit && this.endDate
      }
    },
    data () {
      return {
        orgUnit: {},
        preselectedUnit: {},
        endDate: ''
      }
    },
    mounted () {
      EventBus.$on('organisation-unit-changed', selectedUnit => {
        this.preselectedUnit = selectedUnit
      })
    },
    methods: {
      endOrganisationUnit () {
        let vm = this
        Organisation.endOrganisationUnit(this.orgUnit, this.endDate)
        .then(response => {
          vm.$refs.orgUnitEnd.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>