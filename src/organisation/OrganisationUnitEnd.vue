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
        v-model="validFrom"
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
  import OrganisationUnit from '../api/OrganisationUnit'
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
        return this.orgUnit && this.validFrom
      }
    },
    data () {
      return {
        orgUnit: {},
        preselectedUnit: {},
        validFrom: null
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
        OrganisationUnit.terminate(this.orgUnit, this.validFrom)
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