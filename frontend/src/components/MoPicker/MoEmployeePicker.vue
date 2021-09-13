SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <label>{{ label }}</label>
    <!-- <v-autocomplete
      name="employee-picker"
      :data-vv-as="$tc('input_fields.employee')"
      :items="orderedListOptions"
      v-model="item"
      :get-label="getLabel"
      :component-item="template"
      @item-selected="$emit('input', $event)"
      @update-items="updateItems"
      :auto-select-one-item="false"
      :min-len="2"
      :placeholder="$t('input_fields.search_for_employee')"
      v-validate="validations"
    /> -->
    <mo-autocomplete
        :search="updateItems"
        :getResultValue="getResultValue"
        :onSubmit="selected"
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
import MoAutocomplete from '@/components/MoAutocomplete/MoAutocomplete.vue'
import store from '@/store'
import { Conf } from '@/store/actions/conf'
import Autocomplete from '@/api/Autocomplete'



import sortBy from 'lodash.sortby'
import Search from '@/api/Search'
//import VAutocomplete from 'v-autocomplete'
//import 'v-autocomplete/dist/v-autocomplete.css'
//import MoSearchBarTemplate from '@/components/MoSearchBar/MoSearchBarTemplate'

export default {
  name: 'MoEmployeePicker',

  components: {
    /* TODO: Use `MoAutocomplete` instead which relies on a better third party
     * autocomplete widget. */
    MoAutocomplete,
    //VAutocomplete
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: '$validator'
  },

  props: {
    value: Object,
    required: Boolean,
    /**
     * Validities, used for validation
     */
    validity: Object,
    /**
     * An object of additional validations to be performed
     */
    extraValidations: Object,
    /**
     * Defines a default label name.
     */
    label: {
      type: String,
      default: function() {
          return this.$tc('input_fields.employee')
      }
    }
  },

  data () {
    return {
      item: null,
      items: [],
      template: MoSearchBarTemplate,
      routeName: ''
    }
  },

 /*  computed: {
    orderedListOptions () {
      return sortBy(this.items, 'name')
    },
    validations () {
      let validations = {
        required: this.required,
        employee: [this.validity]
      }
      if (this.extraValidations) {
        validations = { ...validations, ...this.extraValidations }
      }
      return validations
    }
  }, */

  watch: {
    /* item (newVal) {
      this.$validator.validate('employee-picker')
      this.$emit('input', newVal)
    } */
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
/*     updateItems (query) {
      let vm = this
      let org = this.$store.state.organisation
      Search.employees(org.uuid, query)
        .then(response => {
          vm.items = response
        })
    } */

    /**
     * Update employee or organisation suggestions based on search query.
     */
    updateItems (query) {
      let vm = this
      let org = this.$store.state.organisation
      let conf = store.getters[Conf.getters.GET_CONF_DB]

      return new Promise(resolve => {
        var req

        if (query.length < 2) {
          return resolve([])
        }

          if (conf.confdb_autocomplete_use_new_api) {
            req = Autocomplete.employees(query)
          } else {
            req = Search.employees(org.uuid, query)
          }
        
        req.then(response => { resolve(sortBy(response, 'name')) })
      })
    },

    getResultValue (result) {
      return result.name
    },

    /**
     * Go to the selected route.
     */
    selected (item) {
      if (item.uuid == null) return
      this.items = []
      this.$router.push({ name: this.routeName, params: { uuid: item.uuid } })
    }
  },

  created () {
    this.item = this.value
  }
}
</script>

<style scoped>
  /**
   * Style search input. Note: these styles are used both in the top nav bar
   * and also in the search input on the employee index view.
   */
  .search {
    display: flex;
    padding: 0;
  }
  .search .input-group {
    align-items: center; /* vertically center items inside input group */
    flex-wrap: nowrap;
    width: auto;
  }
  .search .input-group.date-input {
    max-width: 10vw;
  }
  .search .input-group.date-input .form-group {
    margin: 0;
  }

  /**
   * Style date picker for 'atDate'.
   */
  .input-group.date-input {
    margin: 0 0 0 0.5vw;
  }
</style>
