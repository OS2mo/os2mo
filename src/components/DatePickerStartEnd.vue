<template>
  <div class="form-row">
    <date-picker 
      class="col"
      label="Startdato"
      v-model="validFrom"
      :disabled-from="validTo"
      required
      @input="updateDate()"
    />

    <date-picker 
      label="Slutdato"
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
      value: Object
    },
    data () {
      return {
        validFrom: null,
        validTo: null
      }
    },
    methods: {
      updateDate () {
        let obj = {}
        if (this.validFrom) {
          obj.from = this.validFrom
        }

        if (this.validTo) {
          obj.to = this.validTo
        }

        this.$emit('input', obj)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>