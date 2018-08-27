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
import Search from '@/api/Search'
import VAutocomplete from 'v-autocomplete'
import 'v-autocomplete/dist/v-autocomplete.css'
import MoAddressSearchTemplate from './MoAddressSearchTemplate.vue'

export default {
  name: 'MoAddressSearchField',
  inject: {
    $validator: '$validator'
  },
  components: {
    VAutocomplete
  },
  props: {
    value: Object,
    label: String,
    global: Boolean
  },
  data () {
    return {
      addressSuggestions: [],
      template: MoAddressSearchTemplate,
      selectedItem: null
    }
  },
  computed: {
    nameId () {
      return 'address-search-field-' + this._uid
    }
  },
  watch: {
    selectedItem (val) {
      this.$emit('input', val)
    }
  },
  created () {
    this.selectedItem = this.value
  },
  methods: {
    getLabel (item) {
      return item ? item.location.name : ''
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
    }
  }
}
</script>
