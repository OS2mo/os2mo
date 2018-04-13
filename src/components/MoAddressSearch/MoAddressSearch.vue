<template>
  <div class="form-row">
    <mo-address-search-field v-model="address" :global="global"/>
    <label class="form-check-label">
      <input class="form-check-input" type="checkbox" v-model="global"/> 
      Søg i hele landet
    </label>
  </div>
</template>

<script>
  import MoAddressSearchField from './MoAddressSearchField'

  export default {
    components: {
      MoAddressSearchField
    },
    props: {
      value: Object
    },
    data () {
      return {
        address: {},
        global: false
      }
    },
    watch: {
      address (val) {
        this.$emit('input', val)
      }
    },
    created () {
      this.address = this.value
    }
  }
</script>
