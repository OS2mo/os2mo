<template>
  <div>
    <div class="form-group">
      <date-picker-start-end v-model="entry.validity"/>
    </div>
    <div class="form-row" v-if="entry.address_type != null">
      <div class="form-group col">
        <mo-facet-picker facet="address_type" v-model="entry.address_type"/>
      </div>

      <div class="form-group col">
        <label>{{entry.address_type.name}}</label>
        <mo-address-search v-if="entry.address_type.scope=='DAR'" v-model="entry.value"/>

        <input v-if="entry.address_type.scope!='DAR'" v-model="entry.value" type="text" class="form-control">
      </div>
    </div>
  </div>
</template>


<script>
import MoAddressSearch from '@/components/MoAddressSearch/MoAddressSearch'
import MoFacetPicker from '@/components/MoFacetPicker'
import DatePickerStartEnd from '@/components/DatePickerStartEnd'

export default {
  name: 'MoAddressEntry',
  components: {
    MoAddressSearch,
    MoFacetPicker,
    DatePickerStartEnd
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
      }
    }
  },
  watch: {
    entry: {
      handler (val) {
        this.$emit('input', val)
      },
      deep: true
    }
  }
}
</script>

<style scoped>
  .input-margin {
    margin-top: 10
  }
</style>