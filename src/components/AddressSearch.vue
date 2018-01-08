<template>
  <div class="form-row">
    <div class="form-group col">
      <label for="exampleFormControlInput1">Adressesøg</label>
      <v-autocomplete 
        :items="addressSuggestions"
        
        :get-label="getLabel" 
        :component-item="template" 
        @update-items="getGeographicalLocation"
        @blur="addressSuggestions=[]"
        @input="updateAddress"
      />
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

    <div class="form-group col">
      <label for="exampleFormControlInput1">Lokationsnavn</label>
      <input 
        type="text" 
        class="form-control" 
        id="" 
        placeholder="" 
        v-model="location.name"  
        @input="updateAddress">
    </div>
  </div>
</template>


<script>
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import template from './AddressSearchTemplate.vue'
  import Property from '../api/Property'

  /**
   * An address search component
   * @author Anders Jepsen
   */

  export default {
    components: {
      VAutocomplete
    },
    props: {
      /**
       * The organisation uuid used to search locally
       */
      localUuid: {
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
        template: template,
        searchCountry: false
      }
    },
    methods: {
      getLabel (item) {
        try {
          this.location.location = item
          return item.vejnavn
        } catch (e) {
          // console.log(e)
        }
      },
      getGeographicalLocation: function (text) {
        let vm = this
        let local = this.localUuid !== '' && !this.searchCountry ? this.localUuid : ''
        Property.getGeographicalLocation(text, local).then(function (response) {
          vm.addressSuggestions = response
        })
      },
      updateAddress: function () {
        try {
          this.$emit('input', {
            location: this.location.location,
            name: this.location.name
          })
        } catch (e) {
          // console.log(e)
        }
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
  .v-autocomplete {
    .v-autocomplete-input-group {
      .v-autocomplete-input {
        display: block;
        width: 100%;
        padding: 0.375rem 0.75rem;
        font-size: 1rem;
        line-height: 1.5;
        color: #495057;
        background-color: #fff;
        background-image: none;
        background-clip: padding-box;
        border: 1px solid #ced4da;
        border-radius: 0.25rem;
        transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
      }
    }
    .v-autocomplete-list {
      z-index: 999;
      background-color: #fff;
      width: 100%;
      padding: 0.375rem 0.75rem;
      border: 1px solid #ced4da;
      border-radius: 0 0 0.25rem;
      transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
      .v-autocomplete-list-item {
        height: 30px;
      }
    }
  }
</style>