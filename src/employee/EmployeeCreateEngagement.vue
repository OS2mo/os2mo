<template>
  <div>
      <h4>Engagement</h4>
      <date-start-end v-model="engagement.validity"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="engagement.org_unit"
        />
        <job-function-picker 
          :org="org" 
          v-model="engagement.job_function"
        />
        <engagement-type-picker 
          :org="org" 
          v-model="engagement.engagement_type"
        />
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
import JobFunctionPicker from '../components/JobFunctionPicker'
import EngagementTypePicker from '../components/EngagementTypePicker'

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
    }
  },
  data () {
    return {
      engagement: {
        type: 'engagement'
      }
    }
  },
  watch: {
    engagement (newVal, oldVal) {
      this.$emit('input', newVal)
    }
  }
}
</script>
