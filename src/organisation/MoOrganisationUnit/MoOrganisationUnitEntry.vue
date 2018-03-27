<template>
  <div>
      <date-start-end v-model="orgUnit.validity"/>

      <div class="form-row">
      <div class="form-group col">
        <label for="">Navn</label>
        <input 
          v-model="orgUnit.name" 
          type="text" 
          class="form-control" 
        >
      </div>
      
      <mo-facet-picker 
        facet="org_unit_type" 
        v-model="orgUnit.org_unit_type"
      />
      </div>
      
      <organisation-unit-picker 
        v-model="orgUnit.parent"
        :is-disabled="disableOrgUnitPicker"
      />
      
      <div class="form-row">
        <div class="form-group col-4">
          <mo-facet-picker 
            facet="address_type" 
            v-model="addresses.address_type"
          />
        </div>

        <div class="form-group col-8">
          <label>{{addresses.address_type.name}}</label>
          <address-type-entry
            v-model="addresses.value"
            :address-type="addresses.address_type"
          />
        </div>
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import MoFacetPicker from '../../components/MoFacetPicker'
import AddressTypeEntry from '../../components/AddressTypeEntry'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker,
    AddressTypeEntry
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
      },
      addresses: {
        address_type: {},
        value: ''
      }
    }
  },
  watch: {
    orgUnit: {
      handler (newVal) {
        this.$emit('input', newVal)
        let valid = (Object.keys(newVal).length >= 4 && newVal.validity.from !== undefined && newVal.name !== '')
        this.$emit('is-valid', valid)
      },
      deep: true
    },
    addresses: {
      handler (val) {
        this.orgUnit.addresses = [val]
      },
      deep: true
    }
  },
  created () {
    this.orgUnit = this.value
  }
}
</script>
