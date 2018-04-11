<template>
  <div>
      <mo-date-picker-range v-model="engagement.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <mo-organisation-unit-picker class="col" label="Vælg enhed" v-model="engagement.org_unit"/>
        <mo-facet-picker facet="job_function" v-model="engagement.job_function" required/>
        <mo-facet-picker facet="engagement_type" v-model="engagement.engagement_type" required/>
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
