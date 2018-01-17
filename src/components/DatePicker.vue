<template>
    <div class="form-group col">
      <label for="date-picker">{{label}}</label>
      <div 
        class="input-group" 
        name="date-picker"
      >
        <date-time-picker 
          name="date"
          v-model="date" 
          :config="config" 
          @input="updateDate()"
          v-validate="{ required: true }" 
        />
        <span class="input-group-addon">
          <icon name="calendar"/>
          </span>
      </div>
      <span v-show="errors.has('date')" class="text-danger">{{ errors.first('date') }}</span>
    </div>
</template>

<script>

import DateTimePicker from 'vue-bootstrap-datetimepicker'
import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'

export default {
  components: {
    DateTimePicker
  },
  props: {
    value: String,
    label: {
      default: 'Dato',
      type: String
    },
    minDate: {
      default: null,
      type: String
    }
  },
  data () {
    return {
      date: '',
      config: {
        format: 'DD-MM-YYYY',
        useCurrent: true,
        locale: 'da'
      }
    }
  },
  beforeUpdate () {
    this.setMinDate()
  },
  methods: {
    setMinDate () {
      if (this.minDate) {
        this.config.minDate = this.minDate
      }
    },

    updateDate () {
      this.$emit('input', this.date)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>