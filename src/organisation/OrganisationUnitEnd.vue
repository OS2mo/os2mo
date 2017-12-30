<template>
  <div>
    <div class="form-row">
      <organisation-unit-picker label="Enhed" class="col"/>
      <date-picker label="Slutdato"/>
    </div>

    <div class="float-right">
      <button-submit/>
    </div>
  </div>
</template>

<script>
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
      return {}
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>