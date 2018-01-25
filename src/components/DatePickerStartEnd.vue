<template>
  <div class="form-row">
    <date-picker 
      class="col"
      label="Startdato"
      v-model="startDate"
      :value="startDate"
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
    props: {
      value: null,
      preselected: {}
    },
    data () {
      return {
        startDate: null,
        endDate: null
      }
    },
    created () {
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