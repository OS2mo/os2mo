SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>

      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-alt"/>
        {{employee.name}}
      </h4>

      <div class="row">
        <div class="col"></div>
      </div>


    </div>
  </div>
</template>

<script>
/**
 * A engagement detail component.
 */

import { EventBus, Events } from '@/EventBus'
import MoLoader from '@/components/atoms/MoLoader'
import { mapState, mapGetters } from 'vuex'
import { Employee } from '@/store/actions/employee'
import { AtDate } from '@/store/actions/atDate'

export default {
  components: {
    MoLoader
  },

  data () {
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
      route: 'route'
    }),

    ...mapGetters({
      employee: Employee.getters.GET_EMPLOYEE,
      atDate: AtDate.getters.GET,
    }),

  },

  watch: {
    atDate (newVal) {
      this._atDate = newVal
      if (this.latestEvent) {
        this.loadContent(this.latestEvent)
      }
    },
  },

  created () {
    this.$store.commit(Employee.mutations.RESET_EMPLOYEE)
    this.$store.dispatch(Employee.actions.SET_EMPLOYEE, this.$route.params.uuid)
  },

  mounted () {
    this._atDate = this.$store.getters[AtDate.getters.GET]
    EventBus.$on(Events.EMPLOYEE_CHANGED, this.listener)
  },

  beforeDestroy () {
    EventBus.$off(Events.EMPLOYEE_CHANGED, this.listener)
  },

  methods: {
    loadContent (event) {
      event.atDate = this._atDate
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
