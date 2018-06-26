<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-search
        class="col" 
        :label="$t('input_fields.choose_unit')" 
        v-model="entry.org_unit"
        required
      />  
      <mo-facet-picker facet="job_function" v-model="entry.job_function" required/>
      <mo-facet-picker facet="engagement_type" v-model="entry.engagement_type" required/>
    </div>
    <mo-date-picker-range 
      v-model="entry.validity" 
      :initially-hidden="datePickerHidden"
      :disabled-dates="orgUnitValidity"
    />
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitSearch from '@/components/MoOrganisationUnitSearch/MoOrganisationUnitSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitSearch,
    MoFacetPicker
  },
  props: {
    value: Object,
    validity: Object
  },
  data () {
    return {
      entry: {}
    }
  },
  computed: {
    datePickerHidden () {
      return this.validity != null
    },
    orgUnitValidity () {
      if (this.entry.org_unit) {
        return this.entry.org_unit.validity
      }
      return {}
    }
  },
  watch: {
    entry: {
      handler (newVal) {
        newVal.type = 'engagement'
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
