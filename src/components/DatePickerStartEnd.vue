<template>
  <div class="form-row">
    <date-picker 
      class="col"
      label="Startdato"
      v-model="startDate"
      @input="updateDate()"
    />

    <date-picker 
      label="Slutdato"
      v-model="endDate"
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
        startDate: '',
        endDate: ''
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