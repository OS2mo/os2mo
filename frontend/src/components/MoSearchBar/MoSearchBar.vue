SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div class="search">
    <div class="input-group">
      <div class="input-group-prepend">
        <span class="input-group-text"><icon name="search"/></span>
      </div>
      <v-autocomplete
        :items="orderedListOptions"
        v-model="item"
        :get-label="getLabel"
        :component-item="template"
        @item-selected="selected"
        @update-items="updateItems"
        :auto-select-one-item="false"
        :min-len="2"
        :placeholder="$t('common.search')"
        class="search-bar"
      />
    </div>
    <div class="input-group date-input">
      <mo-input-date
        v-if="!hideDateInput"
        v-model="atDate"
        v-bind:clear-button="false"
      />
    </div>
  </div>
</template>

<script>
/**
 * A searchbar component.
 */

import sortBy from 'lodash.sortby'
import Search from '@/api/Search'
import VAutocomplete from 'v-autocomplete'
import 'v-autocomplete/dist/v-autocomplete.css'
import MoSearchBarTemplate from './MoSearchBarTemplate'
import { MoInputDate } from '@/components/MoInput'
import { AtDate } from '@/store/actions/atDate'

export default {
  name: 'MoSearchBar',

  components: {
    VAutocomplete,
    MoInputDate
  },

  props: {
    'hideDateInput': Boolean
  },

  data () {
    return {
      /**
       * The item, items, routeName component value.
       * Used to detect changes and restore the value.
       */
      item: null,
      items: [],
      routeName: '',

      atDate: new Date(),

      /**
       * The template component value.
       * Used to add MoSearchBarTemplate to the v-autocomplete.
       */
      template: MoSearchBarTemplate,

      /**
       * The noItem component value.
       * Used to give a default name.
       */
      noItem: [{ name: this.$t('alerts.no_search_results') }]
    }
  },

  computed: {
    orderedListOptions () {
      return sortBy(this.items, 'name')
    }
  },

  watch: {
    /**
     * Whenever route change update.
     */
    '$route' (to) {
      this.getRouteName(to)
    },

    /**
     * Whenever date picker is used, update the 'atDate' Vuex state
     */
    atDate (newVal) {
      // MoInputDate emits two changes for each user interaction with the
      // date picker: one with a Date object attached, and one with a string
      // attached. We are only interested in the string event, as it represents
      // a date with the time portion removed.
      if (typeof(newVal) === 'string') {
        this.$store.dispatch(AtDate.actions.SET, newVal)
      }
    }
  },

  created () {
    /**
     * Called synchronously after the instance is created.
     * Get route name.
     */
    this.getRouteName(this.$route)
  },

  methods: {
    /**
     * Get label name.
     */
    getLabel (item) {
      return item ? item.name : null
    },

    /**
     * Get to the route name.
     * So if we're viewing an employee, it goes to the employee detail.
     */
    getRouteName (route) {
      if (route.name.indexOf('Organisation') > -1) {
        this.routeName = 'OrganisationDetail'
      }
      if (route.name.indexOf('Employee') > -1) {
        this.routeName = 'EmployeeDetail'
      }
    },

    /**
     * Update employee or organisation suggestions based on search query.
     */
    updateItems (query) {
      let vm = this
      vm.items = []
      let org = this.$store.state.organisation
      if (vm.routeName === 'EmployeeDetail') {
        Search.employees(org.uuid, query)
          .then(response => {
            vm.items = response.length > 0 ? response : vm.noItem
          })
      }
      if (vm.routeName === 'OrganisationDetail') {
        Search.organisations(org.uuid, query, this.atDate)
          .then(response => {
            vm.items = response.length > 0 ? response : vm.noItem
          })
      }
    },

    /**
     * Go to the selected route.
     */
    selected (item) {
      if (item.uuid == null) return
      this.items = []
      this.$router.push({ name: this.routeName, params: { uuid: item.uuid } })
    }
  }
}
</script>

<style scoped>
  .search {
    display: flex;
    padding: 0 2.5vw;
  }
  .search .input-group {
    align-items: center; /* vertically center items inside input group */
    width: auto;
    height: 5vh;
  }
  .search .input-group input {
    width: 1%;
  }
  .search .input-group .input-group-prepend {
    flex: unset;
  }
  .search .input-group .input-group-prepend .input-group-text {
    display: inline;
  }
  .search .input-group.date-input {
    max-width: 10vw;
    margin-left: 0.5vw;
  }
  .search .input-group.date-input .form-group {
    margin: 0;
  }
</style>
