<template>
  <div class="col">
      <h1>{{ msg }}</h1>
      <div class="form-row">
        <date-picker label="Slutdato"/>
      </div>
      <div class="float-right">
        <button-submit/>
      </div>
  </div>
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
        msg: 'Afslut medarbejder'
      }
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>