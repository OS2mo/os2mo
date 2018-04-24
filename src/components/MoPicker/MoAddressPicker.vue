<template>
  <span>
    <mo-loader v-show="isLoading"/>
    <div class="col no-address" v-show="!isLoading && noAddresses && orgUnit">Ingen adresser er tilknyttet til enheden</div>
    <div class="form-group" v-show="!isLoading && !noAddresses">
      <label :for="nameId">{{label}}</label>
      <select
        class="form-control col" 
        v-model="selected"
        :name="nameId"
        :id="nameId"
        :disabled="isDisabled"
        :noAddresses="noAddresses"
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
    </div>
  </span>
</template>

<script>
import OrganisationUnit from '@/api/OrganisationUnit'
import MoLoader from '@/components/atoms/MoLoader'

export default {
  name: 'AddressPicker',
  inject: {
    $validator: '$validator'
  },
  components: {
    MoLoader
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
      addresses: [],
      isLoading: false
    }
  },
  computed: {
    nameId () {
      return 'mo-address-picker-' + this._uid
    },

    isDisabled () {
      return this.orgUnit == null
    },

    noAddresses () {
      return this.addresses.length === 0
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
      if (this.orgUnit == null) return
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

<style scoped>
 .no-address {
    margin-top: 2.5rem;
    color: #ff0000;
  }
</style>