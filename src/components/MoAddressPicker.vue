<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <loading v-show="isLoading"/>
    <select
      v-show="!isLoading" 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedAddress()"
    >
      <option disabled>{{label}}</option>
      <option 
        v-for="a in addresses" 
        v-bind:key="a.uuid"
        :value="a"
      >
        {{a.address.name}}
      </option>
    </select>
  </div>
</template>

<script>
import OrganisationUnit from '../api/OrganisationUnit'
import Loading from './Loading'
import { EventBus } from '../EventBus'

export default {
  name: 'AddressPicker',
  components: {
    Loading
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    orgUnit: {
      type: Object,
      required: true
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
    organisationDefined () {
      for (let key in this.orgUnit) {
        if (this.org.hasOwnProperty(key)) {
          return true
        }
      }
      return false
    }
  },
  watch: {
    organisationUnit () {
      this.getAddresses()
    }
  },
  mounted () {
    EventBus.$on('organisation-unit-changed', () => {
      this.getAddresses()
    })
  },
  beforeDestroy () {
    EventBus.$off(['organisation-unit-changed'])
  },
  methods: {
    getAddresses () {
      if (this.organisationDefined) {
        let vm = this
        vm.isLoading = true
        OrganisationUnit.getAddressDetails(this.orgUnit.uuid)
          .then(response => {
            vm.isLoading = false
            vm.addresses = response
          })
      }
    },

    updateSelectedEngagement () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
