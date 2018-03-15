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
    />

    <mo-entry-modal-base
      action="CREATE" 
      type="ORG_UNIT"
      :uuid="uuid" 
      :label="createLabel" 
      :entry-component="entryComponent"
      :content-type="detail"
    />
  </div>
</template>


<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import { EventBus } from '../EventBus'
  import MoTableCollapsibleTense from '../components/MoTableCollapsibleTense'
  import MoEntryModalBase from '../components/MoEntryModalBase'

  export default {
    components: {
      MoTableCollapsibleTense,
      MoEntryModalBase
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
      createLabel: {
        type: String,
        default: 'Opret ny'
      }
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
        this.getAllDetails()
      }
    },
    created () {
      this.getAllDetails()
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
