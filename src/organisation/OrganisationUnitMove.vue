<template>
  <div>
    <h1>{{ msg }}</h1>
    <div class="form-row">
      <date-picker label="Dato for flytning"></date-picker>
    </div>

    <div class="form-row">
      <div class="col">
        <organisation-unit-picker label="Fremsøg enhed"/>
      </div>
      <div class="form-group col">
        <label for="exampleFormControlInput1">Nuværende overenhed</label>
        <input type="email" class="form-control" id="" placeholder="" disabled>
      </div>
    </div>

    <organisation-unit-picker label="Angiv ny overenhed"/>

    <div class="float-right">
      <button-submit/>
    </div> 
  </div>
</template>

<script>
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import DatePicker from '../components/DatePicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      OrganisationUnitPicker,
      DatePicker,
      ButtonSubmit
    },
    data () {
      return {
        msg: 'Flyt enhed'
      }
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>