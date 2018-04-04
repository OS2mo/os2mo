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

      <add-many-components
        :entry-component="addressTypeComponent"
        v-model="addresses"
      />
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import AddressTypeEntry from '../../components/AddressTypeEntry'
import MoFacetPicker from '../../components/MoFacetPicker'
import AddManyComponents from '../../components/AddManyComponents'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker,
    AddressTypeEntry,
    AddManyComponents
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
      addresses: [],
      addressTypeComponent: AddressTypeEntry
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
        this.orgUnit.addresses = val
      },
      deep: true
    }
  },
  created () {
    this.orgUnit = this.value
  },
  methods: {
  }
}
</script>
