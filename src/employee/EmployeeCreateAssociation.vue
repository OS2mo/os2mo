<template>
  <div>
      <h4>Tilknytning</h4>
      <date-start-end v-model="association.validity"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="association.org_unit"
        />
        <job-function-picker 
          :org-uuid="org.uuid" 
          v-model="association.job_function"
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
    }
  },
  data () {
    return {
      association: {
        type: 'association'
      }
    }
  },
  watch: {
    association (newVal, oldVal) {
      this.$emit('input', newVal)
    }
  },
  methods: {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
