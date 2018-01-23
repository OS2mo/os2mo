<template>
    <div class="form-group col">
      <label id="date-label" for="date">{{label}}</label>
      <date-time-picker 
        name="date"
        :data-vv-as="label"
        v-model="date" 
        format="dd-MM-yyyy"
        language="da" 
        monday-first
        bootstrapStyling
        clear-button
        :disabled="disabled"
        @input="updateDate()"
        v-validate="{ 
          date_format: 'dd-MM-yyyy', 
          required: required 
        }"
      />
      <span
        v-show="errors.has('date')" 
        class="text-danger"
      >
        {{ errors.first('date') }}
      </span>
    </div>
</template>

<script>

import DateTimePicker from 'vuejs-datepicker'

export default {
  components: {
    DateTimePicker
  },
  props: {
    value: Date,
    required: Boolean,
    label: {
      default: 'Dato',
      type: String
    },
    disabledTo: {
      default: null,
      type: Date
    }
  },
  data () {
    return {
      date: null,
      disabled: {
        to: null,
        from: null
      }
    }
  },
  watch: {
    disabledTo (newVal, oldVal) {
      this.disabled.to = new Date(newVal)
    }
  },
  methods: {
    updateDate () {
      this.$emit('input', new Date(this.date))
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>