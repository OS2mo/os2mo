<template>
<div class="input-group">
  <div class="input-group-prepend">
    <span class="input-group-text" id="inputGroup-sizing-sm"><icon name="search"/></span>
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
  <!-- <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm"> -->
</div>
  <!-- <div class="input-group">
    <span class="input-group-prepend">
      <icon name="search"/>
    </span>

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
    />
  </div> -->
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

export default {
  name: 'MoSearchBar',

  components: {
    VAutocomplete
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

  components: {
    VAutocomplete
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

      /**
       * The template component value.
       * Used to add MoSearchBarTemplate to the v-autocomplete.
       */
      template: MoSearchBarTemplate,

      /**
       * The noItem component value.
       * Used to give a default name.
       */
      noItem: [{ name: 'Ingen resultater matcher din søgning' }]
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

  watch: {
    /**
     * Whenever route change update.
     */
    '$route' (to) {
      this.getRouteName(to)
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
        Search.organisations(org.uuid, query)
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
  .input-group {
    width: 500px;
  }
  .search-bar {
    flex: 1 1 auto;
    width: 1%;
  }
</style>
