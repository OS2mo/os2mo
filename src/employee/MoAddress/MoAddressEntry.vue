<template>
  <div>
    <date-picker-start-end v-model="entry.validity"/> 
    <div class="form-row">
      <mo-facet-picker facet="address_type" label="Adressetype" v-model="entry.address_type" required/>
    </div>
  </div>
</template>

<script>
import DatePickerStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import MoFacetPicker from '../../components/MoFacetPicker'

export default {
  components: {
    DatePickerStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker
  },
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    }
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
        newVal.type = 'address'
        this.$emit('input', newVal)
        let valid = (Object.keys(newVal).length >= 6 && newVal.validity.from !== undefined)
        this.$emit('is-valid', valid)
      },
      deep: true
    }
  },
  created () {
    this.entry = this.value
  }
}
</script>
