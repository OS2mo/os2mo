SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>

      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-alt"/>
        {{employee.name}} <span class="cpr">({{employee.cpr_no | CPRNumber}})</span>
      </h4>

      <div class="row">
        <div class="col"></div>

        <div class="mr-3">
          <mo-history :uuid="route.params.uuid" type="EMPLOYEE"/>
        </div>
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

import '@/filters/CPRNumber'
import { EventBus, Events } from '@/EventBus'
import EmployeeDetailTabs from './EmployeeDetailTabs'
import MoHistory from '@/components/MoHistory'
import MoLoader from '@/components/atoms/MoLoader'
import { mapState, mapGetters } from 'vuex'
import { Employee } from '@/store/actions/employee'

export default {
  components: {
    EmployeeDetailTabs,
    MoHistory,
    MoLoader
  },

  data () {
    /**
     * The employee, isLoading component value.
     * Used to detect changes and restore the value for columns.
     */
    return {
      isLoading: false,
      latestEvent: undefined
    }
  },

  computed: {
    ...mapState({
      route: 'route'
    }),

    ...mapGetters({
      employee: Employee.getters.GET_EMPLOYEE,
      employeeDetails: Employee.getters.GET_DETAILS
    })
  },

  created () {
    this.$store.commit(Employee.mutations.RESET_EMPLOYEE)
    this.$store.dispatch(Employee.actions.SET_EMPLOYEE, this.$route.params.uuid)
  },
  mounted () {
    EventBus.$on(Events.EMPLOYEE_CHANGED, this.listener)
  },
  beforeDestroy () {
    EventBus.$off(Events.EMPLOYEE_CHANGED, this.listener)
  },
  methods: {
    loadContent (event) {
      this.latestEvent = event
      this.$store.dispatch(Employee.actions.SET_DETAIL, event)
    },
    listener () {
      this.$store.dispatch(Employee.actions.SET_EMPLOYEE, this.$route.params.uuid)
      this.loadContent(this.latestEvent)
    }
  }

}
</script>

<style scoped>
  .cpr {
    color: #aaa
  }
</style>
