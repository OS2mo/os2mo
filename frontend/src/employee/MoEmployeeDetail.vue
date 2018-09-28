<template>
  <div>
    <mo-table-collapsible-tense
      :columns="columns"
      :content="details"
      :content-type="detail"
      :loading="loading"
      :uuid="uuid"
      :edit-component="entryComponent"
      type="EMPLOYEE"
      @shown="getDetails"
    />

    <mo-entry-create-modal 
      type="EMPLOYEE" 
      class="mt-3"
      :uuid="uuid" 
      :entry-component="entryComponent"
    />
  </div>
</template>

<script>
  /**
   * A employeedetail component.
   */

  import Employee from '@/api/Employee'
  import { EventBus } from '@/EventBus'
  import MoTableCollapsibleTense from '@/components/MoTable/MoTableCollapsibleTense'
  import MoEntryCreateModal from '@/components/MoEntryCreateModal'

  export default {
    components: {
      MoTableCollapsibleTense,
      MoEntryCreateModal
    },

    props: {
      /**
       * Defines a unique identifier which must be unique.
       */
      uuid: {type: String, required: true},

      /**
       * Defines the detail content type.
       */
      detail: {type: String, required: true},

      /**
       * Defines columns.
       */
      columns: Array,

      /**
       * Defines a entry component for create.
       */
      entryComponent: Object
    },

    data () {
      return {
      /**
        * The details, loading component value.
        * Used to detect changes and restore the value.
        */
        details: {
          present: [],
          past: [],
          future: []
        },
        loading: {
          present: false,
          past: false,
          future: false
        }
      }
    },

    watch: {
      /**
       * Listener for the time machine.
       */
      uuid () {
        this.getAllDetails()
      }
    },

    mounted () {
      /**
       * When details change update present.
       */
      this.getDetails('present')

      /**
       * Whenever employee details change update.
       */
      EventBus.$on('employee-changed', () => {
        this.getAllDetails()
      })
    },

    methods: {
      /**
       * Let past, present, future be array for getDetails.
       */
      getAllDetails () {
        let tense = ['present', 'future', 'past']

        tense.forEach(t => {
          this.getDetails(t)
        })
      },

      /**
       * Get all employee details.
       */
      getDetails (tense) {
        let vm = this
        vm.loading[tense] = true
        Employee.getDetail(this.uuid, this.detail, tense)
          .then(response => {
            vm.loading[tense] = false
            vm.details[tense] = response
          })
      }
    }
  }
</script>
