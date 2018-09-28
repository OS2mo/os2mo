<template>
  <div class="form-group col">
    <label>{{label}}</label>

    <v-autocomplete 
      v-model="selectedItem"
      :items="addressSuggestions"
      :name="nameId"
      :data-vv-as="label"
      :get-label="getLabel" 
      :component-item="template" 
      @update-items="getGeographicalLocation"
      v-validate="{required: true}"
    />
    
    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>


<script>
  /**
   * A address search field component.
   */

  import Search from '@/api/Search'
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import MoAddressSearchTemplate from './MoAddressSearchTemplate.vue'

  export default {
    name: 'MoAddressSearchField',
  
      /**
       * Validator scope, sharing all errors and validation state.
       */
    inject: {
      $validator: '$validator'
    },

    components: {
      VAutocomplete
    },

    props: {
      /**
       * Create two-way data bindings with the component.
       */
      value: Object,

      /**
       * Defines a label.
       */
      label: String,

      /**
       * This boolean property change it to global search.
       */
      global: Boolean
    },

    data () {
      return {
      /**
        * The addressSuggestions, selectedItem component value.
        * Used to detect changes and restore the value.
        */
        addressSuggestions: [],
        selectedItem: null,

       /**
         * The template component.
         * Used to add MoAddressSearchTemplate component.
         */
        template: MoAddressSearchTemplate
      }
    },

    computed: {
      /**
       * Get name `address-search-field`.
       */
      nameId () {
        return 'address-search-field-' + this._uid
      }
    },

    watch: {
      /**
       * Whenever selectedItem change update val.
       */
      selectedItem (val) {
        this.$emit('input', val)
      }
    },

    created () {
      /**
       * Called synchronously after the instance is created.
       * Set selectedItem to value.
       */
      this.selectedItem = this.value
    },

    methods: {
      /**
       * Get location name.
       */
      getLabel (item) {
        return item ? item.location.name : ''
      },

      /**
       * Update address suggestions based on search query.
       */
      getGeographicalLocation (query) {
        let vm = this
        let org = this.$store.state.organisation
        if (org.uuid === undefined) return
        Search.getGeographicalLocation(org.uuid, query, this.global)
          .then(response => {
            vm.addressSuggestions = response
          })
      }
    }
  }
</script>
