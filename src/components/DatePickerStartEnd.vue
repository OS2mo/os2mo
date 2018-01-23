<template>
  <div class="form-row">
    <date-picker 
      class="col"
      label="Startdato"
      v-model="startDate"
      required
      @input="updateDate()"
    />

    <date-picker 
      label="Slutdato"
      v-model="endDate"
      :disabled-to="startDate"
      @input="updateDate()"
    />
  </div>

</template>

<script>
  import DatePicker from './DatePicker'

  export default {
    components: {
      DatePicker
    },
    props: ['value'],
    data () {
      return {
        startDate: null,
        endDate: null
      }
    },
    created: function () {},
    methods: {
      updateDate () {
        this.$emit('input', {
          startDate: this.startDate,
          endDate: this.endDate
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>