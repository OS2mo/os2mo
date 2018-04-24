<template>
  <div>
    <div class="form-row">
      <mo-address-search-field v-model="address" :label="label" :global="global"/>
      <label class="form-check-label">
        <input class="form-check-input" type="checkbox" v-model="global"/> 
        Søg i hele landet
      </label>
    </div>
  </div>
</template>

<script>
  import MoAddressSearchField from './MoAddressSearchField'

  export default {
    components: {
      MoAddressSearchField
    },
    props: {
      value: Object,
      label: String
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
