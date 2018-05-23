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
        :get-label="getLabel" 
        :component-item='template'
        @update-items="updateItems"
        :auto-select-one-item="false"
        :min-len="2"
        placeholder="Søg efter enhed"
        v-validate="{required: required}"
      />
    </div>

    <span v-show="errors.has(nameId)" class="text-danger">{{ errors.first(nameId) }}</span>
  </div>
</template>

<script>
  import Search from '@/api/Search'
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import MoOrganisationUnitSearchTemplate from './MoOrganisationUnitSearchTemplate'
  
  export default {
    name: 'MoOrganisationUnitSearch',
    components: {
      VAutocomplete
    },
    inject: {
      $validator: '$validator'
    },
    props: {
      value: Object,
      date: Date,
      label: {
        default: 'Angiv overenhed',
        type: String
      },
      required: Boolean
    },
    data () {
      return {
        item: null,
        selectedSuperUnit: null,
        items: [],
        template: MoOrganisationUnitSearchTemplate,
        noItem: [{name: 'Ingen resultater matcher din søgning'}]
      }
    },
    computed: {
      nameId () {
        return 'org-unit-' + this._uid
      }
    },
    watch: {
      selectedSuperUnit (newVal) {
        if (this.selectedSuperUnit == null) return
        this.item = newVal.name
        this.$emit('input', newVal)
      }
    },
    created () {
      this.selectedSuperUnit = this.value
    },
    methods: {
      getLabel (item) {
        return item ? item.name : null
      },

      updateItems (query) {
        let vm = this
        vm.items = []
        let atDate = this.$moment(this.date).format('YYYY-MM-DD')
        let org = this.$store.state.organisation
        Search.organisations(org.uuid, query, atDate)
          .then(response => {
            vm.items = response.length > 0 ? response : vm.noItem
          })
      },

      selected (item) {
        if (item.uuid == null) return
        this.items = []
      }
    }
  }
</script>