<template>
  <div>
    <div class="form-row">
      <mo-facet-picker
        v-show="noPreselectedType"
        class="col"
        :facet="facet"
        v-model="entry.address_type"
        :preselected-user-key="preselectedType"
        required
      />

      <div class="form-group col">
        <div v-if="entry.address_type">
          <mo-address-search
            v-if="isDarAddress"
            :label="entry.address_type.name"
            v-model="address"
            required
          />
          <label :for="identifier" v-if="!isDarAddress">{{entry.address_type.name}}</label>
          <input
            :name="identifier"
            :id="identifier"
            v-if="!isDarAddress"
            :data-vv-as="entry.address_type.name"
            v-model.trim="contactInfo"
            type="text"
            class="form-control"
            v-validate="validityRules"
          >
        </div>
        <span v-show="errors.has(identifier)" class="text-danger">
          {{ errors.first(identifier) }}
        </span>
      </div>

        <mo-facet-picker
          v-if="isPhone"
          v-show="noPreselectedType"
          facet="address_property"
          v-model="entry.visibility"
          :preselected-user-key="preselectedType"
        />
    </div>

    <mo-input-date-range
      class="address-date"
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="disabledDates"
    />
  </div>
</template>

<script>
/**
 * A address entry component.
 */

import MoAddressSearch from '@/components/MoAddressSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import { MoInputDateRange } from '@/components/MoInput'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,
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
    MoInputDateRange
  },

  props: {
    /**
     * This boolean property requires a selected address type.
     * @type {Boolean}
     */
    required: Boolean,

    /**
     * Defines a label.
     * @type {String}
     */
    label: String,

    /**
     * Defines a preselectedType.
     * @type {String}
     */
    preselectedType: String,

    /**
     * Defines a preselectedType.
     * @type {String}
     */
    facet: {
      type: String,
      required: true
    }
  },

  data () {
    return {
      /**
       * The contactInfo, entry, address, addressScope component value.
       * Used to detect changes and restore the value.
       */
      contactInfo: '',
      entry: {},
      address: null,
      addressScope: null
    }
  },

  computed: {
    /**
     * If the address is a DAR.
     * @type {Boolean}
     */
    isDarAddress () {
      if (this.entry.address_type != null) return this.entry.address_type.scope === 'DAR'
      return false
    },

    /**
     * If the address is a PHONE.
     * @type {Boolean}
     */
    isPhone () {
      if (this.entry.address_type != null) return this.entry.address_type.scope === 'PHONE'
      return false
    },

    /**
     * If it has not a preselectedType.
     * @type {Boolean}
     */
    noPreselectedType () {
      return this.preselectedType == null
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
        this.entry.address = { value: newValue }
        this.$emit('input', this.entry)
      }
    },

    /**
     * When entry change, update the newVal.
     */
    entry: {
      handler (newVal) {
        newVal.type = 'address'
        newVal.org = this.$store.getters['organisation/GET_ORGANISATION']
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
          this.entry.value = val.location.uuid
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
    this.contactInfo = this.value.value
  }
}
</script>
