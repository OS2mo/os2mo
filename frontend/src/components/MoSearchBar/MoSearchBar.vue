SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="search">
    <div class="input-group input">
      <mo-autocomplete
        :search="updateItems"
        :getResultValue="getResultValue"
        :onSubmit="selected"
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

import sortBy from "lodash.sortby"
import Autocomplete from "@/api/Autocomplete"
import Search from "@/api/Search"
import MoAutocomplete from "@/components/MoAutocomplete/MoAutocomplete.vue"
import { MoInputDate } from "@/components/MoInput"
import store from "@/store"
import { AtDate } from "@/store/actions/atDate"
import { Conf } from "@/store/actions/conf"

export default {
  name: "MoSearchBar",

  components: {
    MoAutocomplete,
    MoInputDate,
  },

  props: {
    hideDateInput: Boolean,
  },

  data() {
    return {
      item: null,
      routeName: "",
      atDate: new Date(),
    }
  },

  watch: {
    /**
     * Whenever route change update.
     */
    $route(to) {
      this.getRouteName(to)
    },

    /**
     * Whenever date picker is used, update the 'atDate' Vuex state
     */
    atDate(newVal) {
      // MoInputDate emits two changes for each user interaction with the
      // date picker: one with a Date object attached, and one with a string
      // attached. We are only interested in the string event, as it represents
      // a date with the time portion removed.
      if (typeof newVal === "string") {
        this.$store.dispatch(AtDate.actions.SET, newVal)
      }
    },
  },

  created() {
    /**
     * Called synchronously after the instance is created.
     * Get route name.
     */
    this.getRouteName(this.$route)
  },

  methods: {
    /**
     * Get to the route name.
     * So if we're viewing an employee, it goes to the employee detail.
     */
    getRouteName(route) {
      if (route.name.indexOf("Organisation") > -1) {
        this.routeName = "OrganisationDetail"
      }
      if (route.name.indexOf("Employee") > -1) {
        this.routeName = "EmployeeDetail"
      }
    },

    /**
     * Update employee or organisation suggestions based on search query.
     */
    updateItems(query) {
      let vm = this
      let org = this.$store.state.organisation
      let conf = store.getters[Conf.getters.GET_CONF_DB]

      return new Promise((resolve) => {
        var req

        if (query.length < 2) {
          return resolve([])
        }

        if (vm.routeName === "EmployeeDetail") {
          if (conf.autocomplete_use_new_api) {
            req = Autocomplete.employees(query)
          } else {
            req = Search.employees(org.uuid, query)
          }
        }

        if (vm.routeName === "OrganisationDetail") {
          if (conf.autocomplete_use_new_api) {
            req = Autocomplete.organisations(query)
          } else {
            req = Search.organisations(org.uuid, query, this.atDate)
          }
        }

        req.then((response) => {
          resolve(sortBy(response, "name"))
        })
      })
    },

    getResultValue(result) {
      return result.name
    },

    /**
     * Go to the selected route.
     */
    selected(item) {
      if (item.uuid == null) return
      this.items = []
      this.$router.push({ name: this.routeName, params: { uuid: item.uuid } })
    },
  },
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
