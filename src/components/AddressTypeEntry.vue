<template>
  <div class="form-row" v-if="addressType != null">
    <address-search
      v-model="valueType"
      v-if="addressType.scope=='DAR'"
    />
    <div class="form-group col">
      <input
        v-model="valueType"
        type="text" 
        class="form-control"
        v-if="addressType.scope!='DAR'"
        :disabled="isDisabled"
      >
    </div>
  </div>
</template>


<script>
  import AddressSearch from './AddressSearch.vue'

  export default {
    components: {
      AddressSearch
    },
    props: {
      value: [String, Object],
      addressType: {
        type: Object
      },
      item: {
        type: Object
      }
    },
    data () {
      return {
        valueType: '',
        valueAddress: {}
      }
    },
    computed: {
      isDisabled () {
        return !this.addressType.scope
      }
    },
    watch: {
      addressType: {
        handler () {
          this.valueType = null
        },
        deep: true
      },

      valueType: {
        handler (val) {
          this.$emit('input', val)
        },
        deep: true
      }
    },
    methods: {
      selected () {
        this.$emit('input', this.valueType)
      }
    }
  }
</script>
