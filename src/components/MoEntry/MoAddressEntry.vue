<template>
  <div>
    <div class="form-row">
      <div class="form-group col">
        <mo-facet-picker facet="address_type" v-model="entry.address_type" required/>
      </div>

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
    value: Object
  },
  data () {
    return {
      entry: {
        validity: {},
        address_type: {},
        value: null
      },
      address: null
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
        this.entry.value = val.location.uuid
      },
      deep: true
    }
  },
  created () {
    if (this.value.value) {
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
