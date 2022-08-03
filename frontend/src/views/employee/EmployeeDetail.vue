SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading" />

      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-alt" />
        {{ employee.name }}
        <span class="cpr" v-if="showCPR">({{ employee.cpr_no | CPRNumber }})</span>
      </h4>

      <div class="row">
        <div class="col"></div>
      </div>

      <employee-detail-tabs
        :uuid="route.params.uuid"
        :content="employeeDetails"
        @show="loadContent($event)"
      />
    </div>
  </div>
</template>

<script>
/**
 * A employee detail component.
 */

import "@/filters/CPRNumber"
import { EventBus, Events } from "@/EventBus"
import EmployeeDetailTabs from "./EmployeeDetailTabs"
import MoLoader from "@/components/atoms/MoLoader"
import { mapState, mapGetters } from "vuex"
import { Employee } from "@/store/actions/employee"
import { AtDate } from "@/store/actions/atDate"

export default {
  components: {
    EmployeeDetailTabs,
    MoLoader,
  },

  data() {
    /**
     * The employee, isLoading component value.
     * Used to detect changes and restore the value for columns.
     */
    return {
      isLoading: false,
      latestEvent: undefined,
      _atDate: undefined,
    }
  },

  computed: {
    ...mapState({
      route: "route",
    }),

    ...mapGetters({
      employee: Employee.getters.GET_EMPLOYEE,
      employeeDetails: Employee.getters.GET_DETAILS,
      atDate: AtDate.getters.GET,
    }),

    showCPR() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      return conf.show_cpr_no && this.employee.cpr_no
    },
  },

  watch: {
    atDate(newVal) {
      this._atDate = newVal
      if (this.latestEvent) {
        this.loadContent(this.latestEvent)
      }
    },
  },

  created() {
    this.$store.commit(Employee.mutations.RESET_EMPLOYEE)
    this.$store.dispatch(Employee.actions.SET_EMPLOYEE, this.$route.params.uuid)
  },

  mounted() {
    this._atDate = this.$store.getters[AtDate.getters.GET]
    EventBus.$on(Events.EMPLOYEE_CHANGED, this.listener)
  },

  beforeDestroy() {
    EventBus.$off(Events.EMPLOYEE_CHANGED, this.listener)
  },

  methods: {
    loadContent(event) {
      event.atDate = this._atDate
      this.latestEvent = event
      this.$store.dispatch(Employee.actions.SET_DETAIL, event)
    },

    listener() {
      this.$store.dispatch(Employee.actions.SET_EMPLOYEE, this.$route.params.uuid)
      this.loadContent(this.latestEvent)
    },
  },
}
</script>

<style scoped>
.cpr {
  color: #aaa;
}
.card-body {
  padding-right: 3.5rem;
}
</style>
