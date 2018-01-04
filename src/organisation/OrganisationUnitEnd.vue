<template>
  <div>
    <div class="form-row">
      <organisation-unit-picker 
        label="Enhed" 
        class="col"
        v-model="orgUnit"
      />
      <date-picker 
        label="Slutdato"
        v-model="endDate"
      />
    </div>
    <div class="float-right">
      <button-submit @click.native="endOrganisationUnit"/>
    </div>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import DatePicker from '../components/DatePicker'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DatePicker,
      OrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        orgUnit: {},
        endDate: ''
      }
    },
    created: function () {},
    methods: {
      endOrganisationUnit () {
        Organisation.endOrganisationUnit(this.orgUnit, this.endDate)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>