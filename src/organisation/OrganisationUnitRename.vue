<template>
  <b-modal 
    id="orgUnitRename"
    ref="orgUnitRename"  
    size="lg" 
    hide-footer 
    title="Omdøb enhed">
    <div class="form-row">
      <organisation-unit-picker 
        label="Enhed" 
        class="col"
        v-model="orgUnit"
        :preselected="preselectedUnit"
      />
    </div>

    <div class="form-row">
      <div class="form-group col">
        <label for="exampleFormControlInput1">Nyt navn</label>
        <input 
          type="text" 
          class="form-control" 
          id="" 
          v-model="newName"
        >
      </div>
    </div>

    <div class="form-row">
      <date-picker-start-end 
        class="col"
        v-model="dateStartEnd"
      />
    </div>

    <div class="float-right">
      <button-submit @click.native="renameOrganisationUnit"/>
    </div>
  </b-modal>
</template>

<script>
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'
  import DatePickerStartEnd from '../components/DatePickerStartEnd'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import ButtonSubmit from '../components/ButtonSubmit'
  
  export default {
    components: {
      DatePickerStartEnd,
      OrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        orgUnit: {},
        preselectedUnit: {},
        newName: '',
        dateStartEnd: {}
      }
    },
    mounted () {
      EventBus.$on('organisation-unit-changed', selectedUnit => {
        this.preselectedUnit = selectedUnit
      })
    },
    methods: {
      renameOrganisationUnit () {
        let vm = this
        Organisation.renameOrganisationUnit(this.orgUnit, this.newName)
        .then(response => {
          vm.$refs.orgUnitRename.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>