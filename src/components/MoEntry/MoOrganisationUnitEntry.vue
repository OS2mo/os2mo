<template>
  <div>
      <mo-date-picker-range v-model="orgUnit.validity" disable-to-date/>

      <div class="form-row">
        <mo-input :label="$t('input_fields.name')" v-model="orgUnit.name" required/>
        
        <mo-facet-picker facet="org_unit_type" v-model="orgUnit.org_unit_type" required/>
      </div>

      <mo-organisation-unit-search
        v-model="orgUnit.parent"
        required
      />
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitSearch from '@/components/MoOrganisationUnitSearch/MoOrganisationUnitSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoInput from '@/components/atoms/MoInput'
import MoAddMany from '@/components/MoAddMany/MoAddMany'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitSearch,
    MoFacetPicker,
    MoInput,
    MoAddMany
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    disableOrgUnitPicker: Boolean
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
      },
      deep: true
    }
  },
  created () {
    this.orgUnit = this.value
  }
}
</script>
