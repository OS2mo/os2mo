SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div class="search">
    <div class="input-group input">
      <autocomplete
        :search="updateItems"
        :getResultValue="getResultValue"
        @submit="selected"
        :autoSelect=true
        :debounceTime=1
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
import Autocomplete from '@trevoreyre/autocomplete-vue'
import '@trevoreyre/autocomplete-vue/dist/style.css'
import MoSearchBarTemplate from './MoSearchBarTemplate'
import { MoInputDate } from '@/components/MoInput'
import { AtDate } from '@/store/actions/atDate'

export default {
  name: 'MoSearchBar',

  components: {
    Autocomplete,
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
      let org = this.$store.state.organisation

      return new Promise(resolve => {
        if (query.length < 3) {
          return resolve([])
        }

        if (vm.routeName === 'EmployeeDetail') {
          Search.employees(org.uuid, query)
            .then(response => {
              resolve(response)
            })
        }
        if (vm.routeName === 'OrganisationDetail') {
          Search.organisations(org.uuid, query, this.atDate)
            .then(response => {
              resolve(response)
            })
        }
      })
    },

    getResultValue(result) {
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
