<template>
  <div class="form-row">
    <mo-address-search-field v-model="address" :global="global"/>
    <mo-address-search-global v-model="global"/>
  </div>
</template>

<script>
  import MoAddressSearchField from './MoAddressSearchField'
  import MoAddressSearchGlobal from './MoAddressGlobal'

  export default {
    components: {
      MoAddressSearchField,
      MoAddressSearchGlobal
    },
    data () {
      return {
        address: {},
        global: false
      }
    },
    watch: {
      address (val) {
        let addr = val ? val.location.uuid : ''
        this.$emit('input', addr)
      }
    }
  }
</script>
