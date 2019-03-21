<template>
  <div class="card">
    <div class="card-body">
      <mo-loader v-show="isLoading"/>

      <h4 class="card-title" v-show="!isLoading">
        <icon name="user-alt"/>
        {{employee.name}} <span class="cpr">({{employee.cpr_no | CPRNumber}})</span>
      </h4>

      <div class="row">
        <div class="employee-nickname ml-3">
          <h5 class="col-margin ml-4">
            {{employee.nickname}}
          </h5>
          <span class="nickname-text ml-2">
            {{$t('common.nickname')}}
          </span>
        </div>

        <div class="col col-margin ml-1">
          <mo-entry-edit-nickname-modal
            class="nickname-entry"
            :content="employee"
          />
        </div>

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
import MoEntryEditNicknameModal from '@/components/MoEntryEditNicknameModal'

export default {
  components: {
    EmployeeDetailTabs,
    MoHistory,
    MoLoader,
    MoEntryEditNicknameModal
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
    this.$store.dispatch(Employee.actions.SET_EMPLOYEE, this.$route.params.uuid)
  },

  mounted () {
    EventBus.$on(Events.EMPLOYEE_CHANGED, () => {
      this.loadContent(this.latestEvent)
    })
  },

  methods: {
    loadContent (event) {
      this.latestEvent = event
      this.$store.dispatch(Employee.actions.SET_DETAIL, event)
    }
  },
  beforeRouteLeave (to, from, next) {
    this.$store.commit(Employee.mutations.RESET_EMPLOYEE)
    next()
  }

}
</script>

<style scoped>
  .cpr {
    color: #aaa;
  }
  .col-margin {
    margin-top: -1vh;
  }
  .employee-nickname {
    color: #aaa;
  }
  .employee-nickname .nickname-text {
    visibility: hidden;
    width: 10vh;
    background-color: #000000;
    opacity: 0.6;
    color: #fff;
    text-align: center;
    font-size: 1rem;
    border-radius: 6px;
    padding: 3px 0;
    /* Position the tooltip */
    position: absolute;
    z-index: 1;
  }

  .employee-nickname:hover .nickname-text {
    visibility: visible;
  }
</style>
