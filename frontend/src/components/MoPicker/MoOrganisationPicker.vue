<template>
  <div>
    <select 
      class="form-control" 
      id="organisation-picker"
      v-model="selectedOrganisation"
      @change="resetToBaseRoute"
    >
      <option disabled>Vælg organisation</option>
      <option 
        v-for="org in orderedListOptions" 
        :key="org.uuid"
        :value="org"
      >
        {{org.name}}
      </option>
    </select>
  </div>
</template>

<script>
  /**
   * A organisation picker component.
   */

  import Organisation from '@/api/Organisation'
  import { EventBus } from '@/EventBus'

  export default {
    name: 'MoOrganisationPicker',

      /**
       * Validator scope, sharing all errors and validation state.
       */
    inject: {
      $validator: '$validator'
    },

    props: {
      /**
       * Create two-way data bindings with the component.
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
      ignoreEvent: Boolean
    },

    data () {
      return {
      /**
       * The selectedOrganisation, orgs component value.
       * Used to detect changes and restore the value.
       */
        selectedOrganisation: null,
        orgs: []
      }
    },

    computed: {
      orderedListOptions () {
        return this.orgs.slice().sort((a, b) => {
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

    mounted () {
      /**
       * Whenever organisation change update.
       */
      this.getAll()
      EventBus.$on('organisation-changed', newOrg => {
        if (!this.ignoreEvent) this.selectedOrganisation = newOrg
      })
    },

    watch: {
      /**
       * Whenever selected organisation change, update newVal.
       */
      selectedOrganisation (newVal) {
        this.$store.commit(`organisation/setOrg`, newVal)
        Organisation.setSelectedOrganisation(newVal)
        this.$emit('input', newVal)
      },

      /**
       * Whenever atDate change, update.
       */
      atDate () {
        this.getAll()
      }
    },

    methods: {
      /**
       * Get all organisations for this atDate.
       */
      getAll () {
        let vm = this
        Organisation.getAll(this.atDate)
          .then(response => {
            vm.orgs = response
            if (!vm.selectedOrganisation) {
              vm.selectedOrganisation = response[0]
            }
          })
      },

      /**
       * Resets the route back to base.
       * So if we're viewing an employee, it goes back to the employee list.
       */
      resetToBaseRoute () {
        if (this.resetRoute) {
          if (this.$route.name.indexOf('Organisation') > -1) {
            this.$router.push({name: 'Organisation'})
          }
          if (this.$route.name.indexOf('Employee') > -1) {
            this.$router.push({name: 'Employee'})
          }
        }
      }
    }
  }
</script>
