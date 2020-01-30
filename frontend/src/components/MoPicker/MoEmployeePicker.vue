SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
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
      @item-selected="$emit('input', $event)"
      @update-items="updateItems"
      :auto-select-one-item="false"
      :min-len="2"
      :placeholder="$t('input_fields.search_for_employee')"
      v-validate="validations"
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

import sortBy from 'lodash.sortby'
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
    value: Object,
    noLabel: Boolean,
    required: Boolean,
    /**
     * Validities, used for validation
     */
    validity: Object,
    /**
     * An object of additional validations to be performed
     */
    extraValidations: Object
  },

  data () {
    return {
      item: null,
      items: [],
      template: MoSearchBarTemplate
    }
  },

  computed: {
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
  },

  watch: {
    item (newVal) {
      this.$validator.validate('employee-picker')
      this.$emit('input', newVal)
    }
  },

  created () {
    this.item = this.value
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
    }
  }
}
</script>
