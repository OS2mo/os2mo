<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/>
    <div class="form-row">
      <mo-facet-picker facet="address_type" v-model="entry.address_type" required/>
      
      <div class="form-group col">
        <div v-if="entry.address_type != null">
          <mo-address-search v-if="entry.address_type.scope=='DAR'" :label="entry.address_type.name" v-model="address"/>

          <input 
            v-if="entry.address_type.scope!='DAR'" 
            v-model="address.location.uuid" 
            type="text" 
            class="form-control"
            >
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import MoAddressSearch from '@/components/MoAddressSearch/MoAddressSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'

export default {
  name: 'MoAddressEntry',
  components: {
    MoAddressSearch,
    MoFacetPicker,
    MoDatePickerRange
  },
  props: {
    value: Object,
    validity: Object,
    validityHidden: Boolean
  },
  data () {
    return {
      entry: {
        validity: {},
        address_type: {},
        uuid: null
      },
      address: null
    }
  },
  computed: {
    isDarAddress () {
      if (this.entry.address_type != null) return this.entry.address_type.scope === 'DAR'
      return false
    },
    isDisabled () {
      return this.entry.address_type == null
    }
  },
  watch: {
    entry: {
      handler (val) {
        val.type = 'address'
        this.$emit('input', val)
      },
      deep: true
    },

    address: {
      handler (val) {
        if (val == null) return
        this.entry.uuid = val.location.uuid
      },
      deep: true
    }
  },
  created () {
    if (this.value.uuid) {
      this.address = {
        location: {
          name: this.value.name,
          uuid: this.value.value
        }
      }
    }
    this.entry = this.value
  }
}
</script>
