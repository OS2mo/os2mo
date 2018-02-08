<template>
  <div class="form-row">
    <date-picker 
      class="col"
      label="Startdato"
      :preselectedDate="selectedValidFrom"
      v-model="validFrom"
      :disabled-from="validTo"
      required
      @input="updateDate()"
    />

    <date-picker 
      label="Slutdato"
      :preselectedDate="selectedValidTo"
      v-model="validTo"
      :disabled-to="validFrom"
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
      value: Object,
      selectedValidFrom: Date,
      selectedValidTo: Date
    },
    data () {
      return {
        validFrom: null,
        validTo: null
      }
    },
    methods: {
      updateDate () {
        this.$emit('input', {
          from: this.validFrom,
          to: this.validTo
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>