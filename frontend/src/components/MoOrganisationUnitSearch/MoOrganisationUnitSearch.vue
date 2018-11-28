<template>
  <div class="form-group">
    <label :for="nameId">{{ label }}</label>
    <div class="input-group">
      <v-autocomplete 
        :name="nameId"
        :id="nameId"
        data-vv-as="Enhed" 
        :items="items" 
        v-model="selectedSuperUnit" 
        @item-selected="selected"
        :get-label="getLabel" 
        :component-item='template'
        @update-items="updateItems"
        :auto-select-one-item="false"
        :min-len="2"
        placeholder="Søg efter enhed"
        v-validate="{required: required}"
      />
    </div>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
/**
 * A organisation unit search component.
 */

import Search from '@/api/Search'
import VAutocomplete from 'v-autocomplete'
import 'v-autocomplete/dist/v-autocomplete.css'
import MoOrganisationUnitSearchTemplate from './MoOrganisationUnitSearchTemplate'
import moment from 'moment'

export default {
  name: 'MoOrganisationUnitSearch',

  components: {
    VAutocomplete
  },

    /**
     * Validator scope, sharing all errors and validation state.
     */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * Defines a date.
     */
    date: Date,

    /**
     * Defines a label with a default name.
     */
    label: {
      default: 'Angiv overenhed',
      type: String
    },

    /**
     * This boolean property requires a valid unit name.
     */
    required: Boolean
  },

  data () {
    return {
    /**
      * The selectedSuperUnit, items component value.
      * Used to detect changes and restore the value.
      */
      selectedSuperUnit: null,
      items: [],

    /**
      * The template component value.
      * Used to add MoOrganisationUnitSearchTemplate to the autocomplete search.
      */
      template: MoOrganisationUnitSearchTemplate,

    /**
     * The noItem component value.
     * Used to add a default noItem message.
     */
      noItem: [{name: 'Ingen resultater matcher din søgning'}]
    }
  },

  computed: {
    /**
     * Get name `org-unit`.
     */
    nameId () {
      return 'org-unit-' + this._uid
    }
  },

  watch: {
    /**
     * Whenever selectedSuperUnit change, update newVal.
     */
    selectedSuperUnit (newVal) {
      if (this.selectedSuperUnit == null) {
        this.$emit('input', null)
        return
      }
      this.item = newVal.name
      this.$emit('input', newVal)
    }
  },

  created () {
    /**
     * Called synchronously after the instance is created.
     * Set selectedSuperUnit to value.
     */
    if (this.value !== undefined) this.selectedSuperUnit = this.value
  },

  methods: {
    /**
     * Get organisation label name.
     */
    getLabel (item) {
      return item ? item.name : null
    },

    /**
     * Update organisation suggestions based on search query.
     */
    updateItems (query) {
      let vm = this
      vm.items = []
      let atDate = moment(this.date).format('YYYY-MM-DD')
      let org = this.$store.state.organisation
      Search.organisations(org.uuid, query, atDate)
        .then(response => {
          vm.items = response.length > 0 ? response : vm.noItem
        })
    },

    /**
     * Return blank items.
     */
    selected (item) {
      if (item.uuid == null) return
      this.items = []
    }
  }
}
</script>