<template>
  <div>
    <div class="form-row">
      <mo-facet-picker 
        v-show="noPreselectedType"
        facet="address_type" 
        v-model="entry.address_type" 
        :preselected-user-key="preselectedType" 
        required
      />
      
      <div class="form-group col">
        <div v-if="entry.address_type">
          <mo-address-search v-if="entry.address_type.scope=='DAR'" :label="entry.address_type.name" v-model="address"/>
          <label :for="nameId" v-if="entry.address_type.scope!='DAR'">{{entry.address_type.name}}</label>
          <input
            :name="nameId" 
            v-if="entry.address_type.scope!='DAR'"
            :data-vv-as="entry.address_type.name"
            v-model="contactInfo" 
            type="text" 
            class="form-control"
            v-validate="validityRules" 
          >
        </div>
        <span v-show="errors.has(nameId)" class="text-danger">
          {{ errors.first(nameId) }}
        </span>
      </div>
    </div>
  </div>
</template>


<script>
import MoAddressSearch from '@/components/MoAddressSearch/MoAddressSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  name: 'MoManagerAddressPicker',
  inject: {
    $validator: '$validator'
  },
  components: {
    MoAddressSearch,
    MoFacetPicker
  },
  props: {
    value: Object,
    required: Boolean,
    label: String,
    preselectedType: String
  },
  data () {
    return {
      contactInfo: '',
      entry: {
        address_type: {},
        uuid: null,
        value: null
      },
      address: null,
      addressScope: null
    }
  },
  computed: {
    isDarAddress () {
      if (this.entry.address_type != null) return this.entry.address_type.scope === 'DAR'
      return false
    },
    isDisabled () {
      return this.entry.address_type == null
    },
    noPreselectedType () {
      return this.preselectedType == null
    },

    nameId () {
      return 'scope-type-' + this._uid
    },

    validityRules () {
      if (this.entry.address_type.scope === 'PHONE') return {required: true, digits: 8}
      if (this.entry.address_type.scope === 'EMAIL') return {required: true, email: true}
      if (this.entry.address_type.scope === 'EAN') return {required: true, digits: 13}
      if (this.entry.address_type.scope === 'TEXT') return {required: true}
      if (this.entry.address_type.scope === 'WWW') return {required: true, url: true}
      if (this.entry.address_type.scope === 'PNUMBER') return {required: true, numeric: true, min: 5}
      if (this.entry.address_type.scope == null) return {}
    }
  },
  watch: {
    contactInfo: {
      handler (newValue) {
        this.entry.type = 'address'
        this.entry.value = newValue
        this.$emit('input', this.entry)
      }
    },
    entry: {
      handler (newVal) {
        newVal.type = 'address'
        this.$emit('input', newVal)
      },
      deep: true
    },
    address: {
      handler (val) {
        if (val == null) return
        if (this.entry.address_type.scope === 'DAR') {
          this.entry.uuid = val.location.uuid
        } else {
          this.entry.value = val
        }
      },
      deep: true
    }
  }
  // created () {
  //   if (this.value.uuid) {
  //     this.address = {
  //       location: {
  //         name: this.value.name,
  //         uuid: this.value.value
  //       }
  //     }
  //   }
  //   this.entry = this.value
  //   this.contactInfo = this.value.name
  // }
}
</script>
