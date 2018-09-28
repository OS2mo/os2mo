<template>
  <div>
    <label v-if="!noLabel">{{$tc('input_fields.employee')}}</label>
    <v-autocomplete
      name="employee-picker"
      :data-vv-as="$tc('input_fields.employee')"
      :items="orderedListOptions" 
      v-model="item" 
      :get-label="getLabel" 
      :component-item="template" 
      @item-selected="selected"
      @update-items="updateItems"
      :auto-select-one-item="false"
      :min-len="2"
      :placeholder="$t('input_fields.search_for_employee')"
      v-validate="{ required: required }"
    />

    <span v-show="errors.has('employee-picker')" class="text-danger">
      {{ errors.first('employee-picker') }}
    </span>
  </div>
</template>

<script>
  /**
   * A employee picker component.
   */

  import Search from '@/api/Search'
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import MoSearchBarTemplate from '@/components/MoSearchBar/MoSearchBarTemplate'

  export default {
    name: 'MoEmployeePicker',

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
       * This boolean property defines a noLabel value.
       */
      noLabel: Boolean,

      /**
       * This boolean property requires a selected name.
       */
      required: Boolean
    },

    data () {
      return {
        /**
         * The item, items component value.
         * Used to detect changes and restore the value.
         */
        item: null,
        items: [],

        /**
         * The template component value.
         * Used to add MoSearchBarTemplate to the autocomplete search.
         */
        template: MoSearchBarTemplate
      }
    },

    computed: {
      orderedListOptions () {
        return this.items.slice().sort((a, b) => {
          if (a.name < b.name) {
            return -1
          }
          if (a.name > b.name) {
            return 1
          }
          return 0
        })
      }
    },

    methods: {
      /**
       * Get employee name.
       */
      getLabel (item) {
        return item ? item.name : null
      },

      /**
       * Update employees suggestions based on search query.
       */
      updateItems (query) {
        let vm = this
        let org = this.$store.state.organisation
        Search.employees(org.uuid, query)
          .then(response => {
            vm.items = response
          })
      },

      /**
       * Update selected value.
       */
      selected (value) {
        this.$emit('input', value)
      }
    }
  }
</script>
