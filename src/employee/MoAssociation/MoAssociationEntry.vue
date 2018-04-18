<template>
  <div>
      <date-start-end v-model="association.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="association.org_unit"
        />
        <mo-address-picker 
          v-model="association.address" 
          :org-unit="association.org_unit"
        />
      </div>

        <div class="form-row">
        <mo-facet-picker facet="job_function" v-model="association.job_function" required/>
        <mo-facet-picker facet="association_type" v-model="association.association_type" required/>    
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import MoFacetPicker from '../../components/MoFacetPicker'
import MoAddressPicker from '../../components/MoAddressPicker'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker,
    MoAddressPicker
  },
  props: {
    value: Object,
    validity: Object,
    validityHidden: Boolean
  },
  data () {
    return {
      association: {
        validity: {},
        address: {
          name: ''
        }
      }
    }
  },
  watch: {
    association: {
      handler (newVal) {
        newVal.type = 'association'
        if (newVal.address != null) newVal.address_type = newVal.address.address_type
        this.$emit('input', newVal)
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

