<template>
  <div>
      <date-start-end v-model="engagement.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="engagement.org_unit"
        />
        <job-function-picker 
          v-model="engagement.job_function"
        />
        <engagement-type-picker 
          v-model="engagement.engagement_type"
        />
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import JobFunctionPicker from '../../components/JobFunctionPicker'
import EngagementTypePicker from '../../components/EngagementTypePicker'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    JobFunctionPicker,
    EngagementTypePicker
  },
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    },
    validityHidden: Boolean
  },
  data () {
    return {
      engagement: {}
    }
  },
  watch: {
    engagement: {
      handler (newVal) {
        newVal.type = 'engagement'
        this.$emit('input', newVal)
        let valid = (Object.keys(newVal).length >= 5 && newVal.validity.from !== undefined)
        this.$emit('is-valid', valid)
      },
      deep: true
    }
  },
  created () {
    this.engagement = this.value
  }
}
</script>
