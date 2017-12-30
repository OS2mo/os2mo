<template>
  <div>
    <div class="form-row">
      <organisation-unit-picker label="Enhed" class="col"/>
    </div>

    <div class="form-row">
      <div class="form-group col">
        <label for="exampleFormControlInput1">Nyt navn</label>
        <input 
          type="text" 
          class="form-control" 
          id="" 
          v-model="name"
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
      <button-submit/>
    </div> 

    {{dateStartEnd}}
    {{name}}
    {{orgUnit}}
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
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
        name: '',
        dateStartEnd: {}
      }
    },
    beforeUpdate: function () {
      this.getOrganisationUnit()
    },
    methods: {
      getOrganisationUnit () {
        this.orgUnit = Organisation.getSelectedOrganisationUnit()
        this.name = this.orgUnit.name
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>