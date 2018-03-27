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
