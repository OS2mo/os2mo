<template>
  <div class="form-row">
    <div class="form-group col">
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
          v-model="global" 
        /> 
        Søg i hele landet
      </label>
    </div>
  </div>
</template>


<script>
  import Search from '../api/Search'
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import AddressSearchTemplate from './AddressSearchTemplate.vue'

  export default {
    components: {
      VAutocomplete
    },
    inject: {
      $validator: '$validator'
    },
    props: {
      value: [Object, String]
    },
    data () {
      return {
        addressSuggestions: [],
        template: AddressSearchTemplate,
        location: false,
        global: false
      }
    },
    methods: {
      getLabel (item) {
        return item.location.name
      },

      // Update address suggestions based on search query
      getGeographicalLocation (query) {
        let vm = this
        let org = this.$store.state.organisation
        if (org.uuid === undefined) return
        Search.getGeographicalLocation(org.uuid, query, this.global)
          .then(response => {
            vm.addressSuggestions = response
          })
      },

      selected (item) {
        this.$emit('input', item.location.uuid)
      }
    }
  }
</script>
