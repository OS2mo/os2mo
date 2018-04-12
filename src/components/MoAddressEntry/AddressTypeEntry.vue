<template>
<div>
    <div class="form-group">
    <date-picker-start-end v-model="addresses.validity"/>
    </div>
  <div class="form-row" v-if="addresses.address_type != null">

    <div class="form-group col-4">
      <mo-facet-picker 
        facet="address_type" 
        v-model="addresses.address_type"
      />
    </div>

    <div class="form-group col-8">
      <label>{{addresses.address_type.name}}</label>
      <address-search
        v-if="addresses.address_type.scope=='DAR'"
        v-model="addresses.value"
      />

      {{addresses}}
      
      <input
        v-if="addresses.address_type.scope!='DAR'"
        v-model="addresses.value"
        type="text" 
        class="form-control"
        :disabled="isDisabled"
      >
    </div>
  </div>
  </div>
</template>


<script>
  import AddressSearch from '../AddressSearch'
  import MoFacetPicker from '../MoFacetPicker'
  import DatePickerStartEnd from '@/components/DatePickerStartEnd'

  export default {
    components: {
      AddressSearch,
      MoFacetPicker,
      DatePickerStartEnd
    },
    props: {
      value: Object,
      editTypeDisabled: Boolean
    },
    data () {
      return {
        addresses: {
          validity: {},
          address_type: {},
          value: ''
        }
      }
    },
    computed: {
      isDisabled () {
        return !this.addresses.address_type.scope
      }
    },
    watch: {
      addresses: {
        handler (newVal) {
          this.$emit('input', newVal)
        },
        deep: true
      }
    },
    created () {
      if (this.value.name) {
        this.addresses.validity = this.value.validity
        this.addresses.address_type = this.value.address_type
        if (this.value.address_type.scope === 'DAR') {
          this.addresses.value = {location: {}}
          this.addresses.value.location.name = this.value.name
        } else {
          this.addresses.value = this.value.name
        }
      }
    }
  }
</script>

<style scoped>
  .input-margin {
    margin-top: 10
  }
</style>