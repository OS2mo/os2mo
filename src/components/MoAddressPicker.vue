<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedAddress()"
    >
      <option disabled>{{label}}</option>
      <option 
        v-for="a in addresses" 
        :key="a.uuid"
        :value="a"
      >
        ({{a.address_type.name}}) {{a.name}}
      </option>
    </select>
    {{selected}}
  </div>
</template>

<script>
import OrganisationUnit from '../api/OrganisationUnit'

export default {
  name: 'AddressPicker',
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    orgUnit: {
      type: Object
    }
  },
  data () {
    return {
      label: 'Adresser',
      selected: {},
      addresses: []
    }
  },
  watch: {
    orgUnit () {
      this.getAddresses()
    }
  },
  mounted () {
    this.getAddresses()
    this.selected = this.value
  },
  methods: {
    getAddresses () {
      let vm = this
      vm.isLoading = true
      OrganisationUnit.getAddressDetails(this.orgUnit.uuid)
        .then(response => {
          vm.isLoading = false
          vm.addresses = response
        })
    },

    updateSelectedAddress () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
