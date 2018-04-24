<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="datePickerHidden"/>
    <div class="form-row">
      <mo-organisation-unit-picker 
        class="col" 
        label="Vælg enhed" 
        v-model="entry.org_unit"
        required
      />
      <mo-facet-picker facet="role_type" v-model="entry.role_type" required/>
    </div>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
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
        newVal.type = 'role'
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
