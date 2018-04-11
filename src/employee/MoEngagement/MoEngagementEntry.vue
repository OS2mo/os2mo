<template>
  <div>
      <mo-date-picker-range v-model="engagement.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="engagement.org_unit"
        />
        <mo-facet-picker facet="job_function" v-model="engagement.job_function" required/>
        <mo-facet-picker facet="engagement_type" v-model="engagement.engagement_type" required/>
      </div>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import OrganisationUnitPicker from '@/components/OrganisationUnitPicker'
import MoFacetPicker from '@/components/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    OrganisationUnitPicker,
    MoFacetPicker
  },
  props: {
    value: Object,
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
      },
      deep: true
    }
  },
  created () {
    this.engagement = this.value
  }
}
</script>
