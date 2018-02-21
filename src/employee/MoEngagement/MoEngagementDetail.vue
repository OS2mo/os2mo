<template>
  <div>
    <mo-table-collapsible-tense
      :columns="columns"
      :content="details"
      content-type="engagement"
      :loading="loading"
      :uuid="uuid"
      :edit-component="entryComponent"
    />

    <mo-entry-modal-base 
      type="CREATE" 
      :uuid="uuid" 
      label="Nyt engagement" 
      :entry-component="entryComponent"
      content-type="engagement"
    />
  </div>
</template>


<script>
  import Employee from '../../api/Employee'
  import { EventBus } from '../../EventBus'
  import MoTableCollapsibleTense from '../../components/MoTableCollapsibleTense'
  import MoEntryModalBase from '../../components/MoEntryModalBase'
  import MoEngagementEntry from './MoEngagementEntry'

  export default {
    components: {
      MoTableCollapsibleTense,
      MoEntryModalBase
    },
    props: {
      uuid: {
        type: String,
        required: true
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
        },
        columns: ['org_unit', 'job_function', 'engagement_type'],
        entryComponent: MoEngagementEntry
      }
    },
    mounted () {
      EventBus.$on('employee-changed', () => {
        this.getAllDetails()
      })
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
        vm.loading.present = true
        Employee.getEngagementDetails(this.uuid, tense)
        .then(response => {
          vm.loading[tense] = false
          vm.details[tense] = response
        })
      }
    }
  }
</script>
