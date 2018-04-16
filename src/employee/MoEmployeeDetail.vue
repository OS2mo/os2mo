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

    <mo-entry-modal
      class="mt-3"
      action="CREATE"
      type="EMPLOYEE" 
      :uuid="uuid" 
      :label="createLabel" 
      :entry-component="entryComponent"
      :content-type="detail"
    />
  </div>
</template>


<script>
  import Employee from '@/api/Employee'
  import { EventBus } from '@/EventBus'
  import MoTableCollapsibleTense from '@/components/MoTable/MoTableCollapsibleTense'
  import MoEntryModal from '@/components/MoEntryModal'

  export default {
    components: {
      MoTableCollapsibleTense,
      MoEntryModal
    },
    props: {
      uuid: {type: String, required: true},
      detail: {type: String, required: true},
      columns: Array,
      entryComponent: Object,
      createLabel: {type: String, default: 'Opret ny'}
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
      this.getDetails('present')
      EventBus.$on('employee-changed', () => {
        this.getAllDetails()
      })
    },
    methods: {
      getAllDetails () {
        let tense = ['present', 'future', 'past']

        tense.forEach(t => {
          this.getDetails(t)
        })
      },

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
