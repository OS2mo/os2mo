<template>
  <div class="form-row">
    <date-picker 
      class="col"
      label="Startdato"
      v-model="startDate"
      :preselectedDate="selectedValidFrom"
      required
      @input="updateDate()"
    />

    <date-picker 
      label="Slutdato"
      v-model="endDate"
      :disabled-to="startDate"
      :preselectedDate="selectedValidTo"
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
    props: {
      value: null,
      preselectedDate: Date,
      selectedValidFrom: Date,
      selectedValidTo: Date
    },
    data () {
      return {
        startDate: null,
        endDate: null,
        dates: {
          startDate: null,
          endDate: null
        }
      }
    },
    created () {
      this.dates = {
        startDate: this.selectedValidFrom,
        endDate: this.selectedValidTo
      }
    },
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