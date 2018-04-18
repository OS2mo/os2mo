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

    <mo-entry-modal
      class="mt-3"
      action="CREATE" 
      type="ORG_UNIT"
      :uuid="uuid" 
      :label="createLabel" 
      :entry-component="entryComponent"
      :content-type="detail"
      v-if="!hideCreate"
    />
  </div>
</template>


<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import { EventBus } from '@/EventBus'
  import MoTableCollapsibleTense from '@/components/MoTable/MoTableCollapsibleTense'
  import MoEntryModal from '@/components/MoEntryModal'

  export default {
    components: {
      MoTableCollapsibleTense,
      MoEntryModal
    },
    props: {
      uuid: {
        type: String,
        required: true
      },
      atDate: [Date, String],
      detail: {
        type: String,
        required: true
      },
      columns: Array,
      entryComponent: Object,
      createLabel: String,
      hideCreate: Boolean
    },
    data () {
      return {
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
      EventBus.$on('organisation-unit-changed', () => {
        this.getAllDetails()
      })
    },
    watch: {
      uuid () {
        // listener for the time machine
        this.getAllDetails()
      }
    },
    created () {
      this.getDetails('present')
    },
    beforeDestroy () {
      EventBus.$off(['organisation-unit-changed'])
    },
    methods: {
      getAllDetails () {
        let tense = ['past', 'present', 'future']

        tense.forEach(t => {
          this.getDetails(t)
        })
      },

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
