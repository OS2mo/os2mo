<template>
  <div>
    <div class="form-row">
      <mo-facet-picker facet="leave_type" v-model="entry.leave_type" required/>
    </div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="datePickerHidden"/>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    MoFacetPicker
  },
  props: {
    value: Object,
    validity: Object
  },
  data () {
    return {
      entry: {
        validity: {}
      }
    }
  },
  computed: {
    datePickerHidden () {
      return this.validity != null
    }
  },
  watch: {
    entry: {
      handler (newVal) {
        newVal.type = 'leave'
        this.$emit('input', newVal)
      },
      deep: true
    },

    validity (newVal) {
      this.entry.validity = newVal
    }
  },
  created () {
    this.entry = this.value
  }
}
</script>
