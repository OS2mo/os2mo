<template>
<b-modal 
    id="employeeEnd" 
    size="lg" 
    hide-footer 
    title="Afslut medarbejder"
    ref="employeeEnd"
  >
  <div class="col">
      <div class="form-row">
        <date-picker label="Slutdato"/>
      </div>
      <div class="float-right">
        <button-submit/>
      </div>
  </div>
</b-modal>
</template>

<script>
  import DatePicker from '../components/DatePicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DatePicker,
      ButtonSubmit
    },
    data () {
      return {
      }
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>