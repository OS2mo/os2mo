<template>
  <div>
    <div class="form-row">
      <mo-it-system-picker 
        class="select-itSystem" 
        v-model="entry.itsystem" 
        :preselected="entry.uuid"
      />
    </div>

    <mo-date-picker-range 
      v-model="entry.validity" 
      :initially-hidden="validityHidden"
    />
  </div>
</template>

<script>
  import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
  import MoItSystemPicker from '@/components/MoPicker/MoItSystemPicker'

  export default {
    components: {
      MoDatePickerRange,
      MoItSystemPicker
    },

    props: {
      value: Object,
      validityHidden: Boolean
    },

    data () {
      return {
        entry: {
          validity: {}
        }
      }
    },

    watch: {
      entry: {
        handler (newVal) {
          newVal.type = 'it'
          if (newVal.itsystem !== undefined) newVal.uuid = newVal.itsystem.uuid
          this.$emit('input', newVal)
        },
        deep: true
      }
    },

    created () {
      this.entry = this.value
    }
  }
</script>

