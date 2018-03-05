<template>
  <div>
      <date-start-end v-model="association.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="association.org_unit"
        />
        <job-function-picker 
          v-model="association.job_function"
        />
        <association-type-picker 
          v-model="association.association_type"
        />
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import JobFunctionPicker from '../../components/JobFunctionPicker'
import AssociationTypePicker from '../../components/AssociationTypePicker'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    JobFunctionPicker,
    AssociationTypePicker
  },
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    },
    validity: Object,
    validityHidden: Boolean
  },
  data () {
    return {
      association: {
        validity: {}
      }
    }
  },
  watch: {
    association: {
      handler (newVal) {
        newVal.type = 'association'
        this.$emit('input', newVal)
        let valid = false
        if (Object.keys(newVal).length >= 5 && newVal.validity.from !== undefined) valid = true
        this.$emit('is-valid', valid)
      },
      deep: true
    },

    validity (newVal) {
      this.association.validity = newVal
    }
  },
  created () {
    this.association = this.value
  }
}
</script>

