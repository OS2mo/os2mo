<template>
  <div class="form-row" v-if="addresses.address_type != null">
    <div class="form-group col-4">
      <mo-facet-picker 
        facet="address_type" 
        v-model="addresses.address_type"
      />
    </div>

    <div class="form-group col-8">
      <label>{{entryLabel}}</label>
      <address-search
        v-model="addresses.value"
        v-if="addresses.address_type.scope=='DAR'"
      />

      <input
        v-model="addresses.value"
        type="text" 
        class="form-control"
        v-if="addresses.address_type.scope!='DAR'"
        :disabled="isDisabled"
      >
    </div>
  </div>
</template>


<script>
  import AddressSearch from './AddressSearch'
  import MoFacetPicker from './MoFacetPicker'

  export default {
    components: {
      AddressSearch,
      MoFacetPicker
    },
    props: {
      value: [String, Object, Array],
      item: {
        type: Object
      }
    },
    data () {
      return {
        addresses: {
          address_type: {},
          value: ''
        },
        items: {}
      }
    },
    computed: {
      entryLabel () {
        return this.addresses.address_type.name || '\u00A0'
      },

      isDisabled () {
        return !this.addresses.address_type.scope
      }
    },
    watch: {
      value (val) {
        this.addresses = val
      },
      addresses: {
        handler (val) {
          this.$emit('input', val)
        },
        deep: true
      }
    }
  }
</script>
