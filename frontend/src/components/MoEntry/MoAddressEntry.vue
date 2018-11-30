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
    <mo-date-picker-range
      class="address-date"
      v-model="entry.validity"
      :initially-hidden="validityHidden"
    />
  </div>
</template>

<script>
/**
   * A address entry component.
   */

import MoAddressSearch from '@/components/MoAddressSearch/MoAddressSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'

export default {
  name: 'MoAddressEntry',

  /**
       * Validator scope, sharing all errors and validation state.
       */
  inject: {
    $validator: '$validator'
  },

  components: {
    MoAddressSearch,
    MoFacetPicker,
    MoDatePickerRange
  },

  props: {
    /**
       * Create two-way data bindings with the component.
       */
    value: Object,

    /**
       * This boolean property hides the validity dates.
       */
    validityHidden: Boolean,

    /**
       * This boolean property requires a selected address type.
       */
    required: Boolean,

    /**
       * Defines a label.
       */
    label: String,

    /**
       * Defines a preselectedType.
       */
    preselectedType: String
  },

  data () {
    return {
      /**
        * The contactInfo, entry, address, addressScope component value.
        * Used to detect changes and restore the value.
        */
      contactInfo: '',
      entry: {
        validity: {},
        address_type: {},
        uuid: null,
        value: null
      },
      address: null,
      addressScope: null
    }
  },

  computed: {
    /**
       * If the address is a DAR.
       */
    isDarAddress () {
      if (this.entry.address_type != null) return this.entry.address_type.scope === 'DAR'
      return false
    },

    /**
       * Disable address type.
       */
    isDisabled () {
      return this.entry.address_type == null
    },

    /**
       * If it has not a preselectedType.
       */
    noPreselectedType () {
      return this.preselectedType == null
    },

    /**
       * Get name `scope-type`.
       */
    nameId () {
      return 'scope-type-' + this._uid
    },

    /**
       * Every scopes validity rules.
       */
    validityRules () {
      if (this.entry.address_type.scope === 'PHONE') return { required: true, digits: 8 }
      if (this.entry.address_type.scope === 'EMAIL') return { required: true, email: true }
      if (this.entry.address_type.scope === 'EAN') return { required: true, digits: 13 }
      if (this.entry.address_type.scope === 'TEXT') return { required: true }
      if (this.entry.address_type.scope === 'WWW') return { required: true, url: true }
      if (this.entry.address_type.scope === 'PNUMBER') return { required: true, numeric: true, min: 5 }
      return {}
    }
  },

  watch: {
    /**
       * Whenever contactInfo change, update entry with a Array.
       */
    contactInfo: {
      handler (newValue) {
        this.entry.type = 'address'
        this.entry.value = newValue
        this.$emit('input', this.entry)
      }
    },

    /**
       * When entry change, update the newVal.
       */
    entry: {
      handler (newVal) {
        newVal.type = 'address'
        this.$emit('input', newVal)
      },
      deep: true
    },

    /**
       * Whenever address change, update.
       */
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
  },

  created () {
    /**
       * Called synchronously after the instance is created.
       * Set entry and contactInfo to value.
       */
    if (this.value.uuid) {
      this.address = {
        location: {
          name: this.value.name,
          uuid: this.value.value
        }
      }
    }
    this.entry = this.value
    this.contactInfo = this.value.name
  }
}
</script>
