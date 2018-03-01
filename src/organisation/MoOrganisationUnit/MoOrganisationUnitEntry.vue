<template>
  <div>
      <date-start-end v-model="orgUnit.validity"/>

      <div class="form-row">
      <div class="form-group col">
        <label for="">Navn</label>
        <input 
          v-model="orgUnit.name" 
          type="text" 
          class="form-control" 
        >
      </div>

      <mo-facet-picker 
      facet="org_unit_type" 
      label="Enhedstype" 
      v-model="orgUnit.org_unit_type"
      />
      </div>

      <organisation-unit-picker 
        v-model="orgUnit.parent"
      />
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import MoFacetPicker from '../../components/MoFacetPicker'

export default {
  components: {
    DateStartEnd,
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
      orgUnit: {
        name: '',
        validity: {}
      }
    }
  },
  watch: {
    orgUnit: {
      handler (newVal) {
        this.$emit('input', newVal)
        let valid = (Object.keys(newVal).length >= 4 && newVal.validity.from !== undefined && newVal.name !== '')
        this.$emit('is-valid', valid)
      },
      deep: true
    }
  },
  created () {
    this.orgUnit = this.value
  }
}
</script>
