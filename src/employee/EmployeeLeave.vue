<template>
  <div>
      <h1>Orlov</h1>
      <div class="form-row">
        <date-picker 
          label="Orlov start"
        />
        <date-picker 
          label="Orlov slut"
        />

        <div class="form-group col">
          <label>Orlovstype</label>
          <select class="form-control col" id="" >
            <option>Orlovstype</option>
          </select>
        </div>        
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
      return {}
    },
    created: function () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>