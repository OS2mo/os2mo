<template>
  <div class="form-row">
    <div class="form-group col">
      <label for="exampleFormControlInput1">Adressesøg</label>
      <v-autocomplete 
        :items="addressSuggestions"
        name="address"
        :get-label="getLabel" 
        :component-item="template" 
        @update-items="getGeographicalLocation"
        @item-selected="selected"
        v-validate="{ required: true }"
      />
      <span v-show="errors.has('address')" class="text-danger">{{ errors.first('address') }}</span>
    </div>

    <div class="form-check col">
      <label class="form-check-label">
        <input 
          class="form-check-input" 
          type="checkbox" 
          v-model="searchCountry" 
        > 
        Søg i hele landet
      </label>
    </div>
  </div>
</template>


<script>
  import Property from '../api/Property'
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import AddressSearchTemplate from './AddressSearchTemplate.vue'

  export default {
    components: {
      VAutocomplete
    },
    props: {
      org: {
        type: Object,
        required: true
      },
      value: Object
    },
    data () {
      return {
        addressSuggestions: [],
        template: AddressSearchTemplate,
        searchCountry: false
      }
    },
    methods: {
      getLabel (item) {
        return item.vejnavn
      },

      // Update address suggestions based on search query
      getGeographicalLocation (query) {
        let vm = this
        let local = this.searchCountry ? '' : this.org.uuid
        Property.getGeographicalLocation(query, local)
        .then(response => {
          vm.addressSuggestions = response
        })
      },

      selected (item) {
        this.$emit('input', item)
      }
    }
  }
</script>
