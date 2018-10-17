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
          <mo-history :uuid="$route.params.uuid" type="EMPLOYEE"/>
        </div>
      </div>

      <employee-detail-tabs 
        :uuid="$route.params.uuid"
        :content="$store.getters['employee/GET_DETAILS']" 
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
  import { EventBus } from '@/EventBus'
  import EmployeeDetailTabs from './EmployeeDetailTabs'
  import MoHistory from '@/components/MoHistory'
  import MoLoader from '@/components/atoms/MoLoader'

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
      employee () {
        return this.$store.getters['employee/GET_EMPLOYEE']
      }
    },

    created () {
      this.$store.dispatch('employee/SET_EMPLOYEE', this.$route.params.uuid)
    },
    mounted () {
      EventBus.$on('employee-changed', () => {
        this.loadContent(this.latestEvent)
      })
    },
    methods: {
      loadContent (event) {
        this.latestEvent = event
        this.$store.dispatch('employee/SET_DETAIL', event)
      }
    },
    beforeRouteLeave (to, from, next) {
      this.$store.commit('employee/RESET_EMPLOYEE')
      next()
    }

  }
</script>

<style scoped>
  .cpr {
    color: #aaa
  }
</style>
