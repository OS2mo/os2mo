<template>
  <div>
      <date-start-end v-model="orgUnit.validity"/>

      <div class="form-row">
      <div class="form-group col">
        <label for="">Navn</label>
        <input 
          v-model="orgUnit.name" 
          data-vv-as="Navn"
          type="text" 
          class="form-control"
          name="unit-name"
          v-validate="{required: true}"
        >
            <span
              v-show="errors.has('unit-name')" 
              class="text-danger"
            >
              {{ errors.first('unit-name') }}
          </span>
      </div>
      
      <mo-facet-picker 
        facet="org_unit_type" 
        v-model="orgUnit.org_unit_type"
        required
      />
      </div>
      
      <organisation-unit-picker 
        v-model="orgUnit.parent"
        :is-disabled="disableOrgUnitPicker"
      />
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import AddressTypeEntry from '@/components/MoAddressEntry/AddressTypeEntry'
import MoFacetPicker from '../../components/MoFacetPicker'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker,
    AddressTypeEntry
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    },
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
