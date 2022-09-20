<!-- SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0 -->

<!-- This component has been hidden. It, however, has sideeffects * which currently prohibit
the component from beeing removed * alltogether, so it has been hidden with
style="display=none" -->
<template>
  <div style="display: none">
    <select
      class="form-control"
      id="organisation-picker"
      v-model="selectedOrganisation"
      @change="resetToBaseRoute"
    >
      <option disabled>{{ $t("input_fields.choose_organisation") }}</option>
      <option v-for="org in orderedListOptions" :key="org.uuid" :value="org">
        {{ org.name }}
      </option>
    </select>
  </div>
</template>

<script>
/**
 * A organisation picker component.
 */

import sortBy from "lodash.sortby"
import Organisation from "@/api/Organisation"
import { EventBus, Events } from "@/EventBus"
import { mapGetters, mapState } from "vuex"
import { Employee } from "@/store/actions/employee"
import { OrganisationUnit } from "@/store/actions/organisationUnit"
import { Organisation as OrgStore } from "@/store/actions/organisation"
export default {
  name: "MoOrganisationPicker",

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  props: {
    /**
     * @model
     */
    value: Object,

    /**
     * Defines a atDate.
     */
    atDate: [Date, String],

    /**
     * This boolean property resets the route.
     */
    resetRoute: Boolean,

    /**
     * This boolean property igonores a event.
     */
    ignoreEvent: Boolean,
  },

  data() {
    return {
      /**
       * The selectedOrganisation, orgs component value.
       * Used to detect changes and restore the value.
       */
      selectedOrganisation: null,
      orgs: [],
    }
  },

  computed: {
    ...mapGetters({
      currentUnit: OrganisationUnit.getters.GET_ORG_UNIT,
      currentEmployee: Employee.getters.GET_EMPLOYEE,
    }),

    ...mapState({
      route: "route",
    }),

    orderedListOptions() {
      return sortBy(this.orgs, name)
    },
  },

  mounted() {
    /**
     * Whenever organisation change update.
     */
    this.getAll()
    EventBus.$on(Events.ORGANISATION_CHANGED, (newOrg) => {
      if (!this.ignoreEvent) this.selectedOrganisation = newOrg
    })
  },

  watch: {
    /**
     * Whenever selected organisation change, update newVal.
     */
    selectedOrganisation(newVal) {
      this.$store.commit(OrgStore.mutations.SET_ORGANISATION, newVal)
      this.$emit("input", newVal)
    },

    currentEmployee: {
      handler(val) {
        if (val.org) {
          if (
            !this.selectedOrganisation ||
            val.org_uuid !== this.selectedOrganisation.uuid
          ) {
            this.selectedOrganisation = val.org
          }
        }
      },
      deep: true,
    },

    currentUnit: {
      handler(val) {
        if (val.org) {
          if (
            !this.selectedOrganisation ||
            val.org_uuid !== this.selectedOrganisation.uuid
          ) {
            this.selectedOrganisation = val.org
          }
        }
      },
      deep: true,
    },

    /**
     * Whenever atDate change, update.
     */
    atDate() {
      this.getAll()
    },
  },

  methods: {
    /**
     * Get all organisations for this atDate.
     */
    getAll() {
      let vm = this
      Organisation.getAll(this.atDate).then((response) => {
        vm.orgs = response

        let org =
          (vm.currentUnit && vm.currentUnit.org) ||
          (vm.currentEmployee && vm.currentEmployee.org) ||
          response[0]

        vm.selectedOrganisation = org
      })
    },

    /**
     * Resets the route back to base.
     * So if we're viewing an employee, it goes back to the employee list.
     */
    resetToBaseRoute() {
      if (this.resetRoute) {
        if (this.route.name.indexOf("Organisation") > -1) {
          this.$router.push({ name: "Organisation" })
        }
        if (this.route.name.indexOf("Employee") > -1) {
          this.$router.push({ name: "Employee" })
        }
      }
    },
  },
}
</script>
