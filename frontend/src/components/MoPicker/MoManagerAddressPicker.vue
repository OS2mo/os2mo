<template>
  <div>
    <div class="form-row">
      <mo-facet-picker
        v-show="noPreselectedType"
        facet="manager_address_type"
        v-model="entry.address_type"
        :preselected-user-key="preselectedType"
        required
      />

      <div class="form-group col">
        <div v-if="entry.address_type">
          <mo-address-search
            v-if="entry.address_type.scope=='DAR'"
            :label="entry.address_type.name"
            v-model="address"
          />

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
/**
   * A manager address picker component.
   */

import MoAddressSearch from '@/components/MoAddressSearch/MoAddressSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  name: 'MoManagerAddressPicker',

  /**
       * Validator scope, sharing all errors and validation state.
       */
  inject: {
    $validator: '$validator'
  },

  components: {
    MoAddressSearch,
    MoFacetPicker
  },

  props: {
    /**
       * Create two-way data bindings with the component.
       */
    value: [Object, Array],

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
      contactInfo: null,
      entry: {
        address_type: {},
        uuid: null,
        value: null
      },
      address: null
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
      if (this.entry.address_type.scope == null) return {}
    }
  },

  watch: {
    /**
       * Whenever contactInfo change, update entry with a Array.
       */
    contactInfo: {
      handler (newVal) {
        this.entry.type = 'address'
        this.entry.value = newVal
        this.$emit('input', [this.entry])
      },
      deep: true
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
          uuid: this.value.uuid
        }
      }
    }
    this.contactInfo = this.value.name
    this.entry = this.value
  }
}
</script>
