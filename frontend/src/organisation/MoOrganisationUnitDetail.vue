<template>
  <div>
    <mo-table-collapsible-tense
      :columns="columns"
      :content="details"
      :content-type="detail"
      :loading="loading"
      :uuid="uuid"
      :edit-component="entryComponent"
      type="ORG_UNIT"
      @shown="getDetails"
    />

    <mo-entry-create-modal
      type="ORG_UNIT"
      class="mt-3"
      :uuid="uuid" 
      :entry-component="entryComponent"
      v-if="!hideCreate"
    />
  </div>
</template>


<script>
  /**
   * A organisation unit detail component.
   */

  import OrganisationUnit from '@/api/OrganisationUnit'
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
      uuid: {
        type: String,
        required: true
      },

      /**
       * Defines a at date.
       */
      atDate: [Date, String],

      /**
       * Defines the detail content type.
       */
      detail: {
        type: String,
        required: true
      },

      /**
       * Defines columns.
       */
      columns: Array,

      /**
       * Defines a entryComponent for create.
       */
      entryComponent: Object,

      /**
       * This Boolean property hides the create button.
       */
      hideCreate: Boolean
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

    mounted () {
      /**
       * Whenever details change update.
       */
      EventBus.$on('organisation-unit-changed', () => {
        this.getAllDetails()
      })
    },

    watch: {
      /**
       * Listener for the time machine.
       */
      uuid () {
        this.getAllDetails()
      }
    },

    created () {
      /**
       * Called synchronously after the instance is created.
       * Show the present detail as default.
       */
      this.getDetails('present')
    },

    beforeDestroy () {
      /**
       * Called right before a instance is destroyed.
       */
      EventBus.$off(['organisation-unit-changed'])
    },

    methods: {
      /**
       * Let past, present, future be array for getDetails.
       */
      getAllDetails () {
        let tense = ['past', 'present', 'future']
        tense.forEach(t => {
          this.getDetails(t)
        })
      },

      /**
       * Get all organisation details.
       */
      getDetails (tense) {
        let vm = this
        vm.loading[tense] = true
        OrganisationUnit.getDetail(this.uuid, this.detail, tense, this.atDate)
          .then(response => {
            vm.loading[tense] = false
            vm.details[tense] = response
          })
      }
    }
  }
</script>
