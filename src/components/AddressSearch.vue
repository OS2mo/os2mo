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
        @untouched="addressSuggestions=[]"
        @input="updateAddress"
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
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import AddressSearchTemplate from './AddressSearchTemplate.vue'
  import Property from '../api/Property'

  export default {
    components: {
      VAutocomplete
    },
    props: {
      /**
       * The organisation uuid used to search locally
       */
      orgUuid: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        location: {
          location: '',
          name: ''
        },
        addressSuggestions: [],
        template: AddressSearchTemplate,
        searchCountry: false
      }
    },
    methods: {
      /**
       * Return the street name of an item and set the location
       * @input item
       */
      getLabel (item) {
        try {
          this.location.location = item
          return item.vejnavn
        } catch (e) {
          console.log(e)
        }
      },

      /**
       * Update address suggestions based on search query
       */
      getGeographicalLocation (query) {
        let vm = this
        let local = this.orgUuid !== '' && !this.searchCountry ? this.orgUuid : ''
        Property.getGeographicalLocation(query, local).then(function (response) {
          vm.addressSuggestions = response
        })
      },

      updateAddress () {
        try {
          this.$emit('updateAddress', {
            location: this.location.location,
            name: this.location.name
          })
        } catch (e) {
          console.log(e)
        }
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">

</style>