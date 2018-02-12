<template>
  <div>
      <h4>Tilknytning</h4>
      <date-start-end v-model="association.validity" initially-hidden/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="association.org_unit"
        />
        <job-function-picker 
          :org-uuid="org.uuid" 
          v-model="association.job_function"
          :org="org"
        />
        <association-type 
          :org-uuid="org.uuid" 
          v-model="association.association_type"
        />
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
import JobFunctionPicker from '../components/JobFunctionPicker'
import AssociationType from '../components/AssociationType'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    JobFunctionPicker,
    AssociationType
  },
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    },
    validity: Object
  },
  data () {
    return {
      association: {
        type: 'association',
        validity: {}
      }
    }
  },
  watch: {
    association (newVal) {
      this.$emit('input', newVal)
    },

    validity (newVal) {
      this.association.validity = newVal
    }
  }
}
</script>

