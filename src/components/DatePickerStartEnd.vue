<template>
  <div class="form-row">
    <div v-show="hidden">
      <button class="btn btn-link" @click="hidden=false">
        Vælg anden validity
      </button>
    </div>
    <date-picker 
      label="Startdato"
      v-model="validFrom"
      v-show="!hidden"
      :disabled-from="validTo"
      @input="updateDate()"
      required
    />

    <date-picker 
      label="Slutdato"
      v-model="validTo"
      v-show="!hidden"
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
      initiallyHidden: Boolean
    },
    data () {
      return {
        validFrom: null,
        validTo: null,
        hidden: false
      }
    },
    watch: {
      value (newVal) {
        if (this.hidden) {
          this.validFrom = newVal.from
          this.validTo = newVal.to
        }
      }
    },
    created () {
      this.hidden = this.initiallyHidden
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