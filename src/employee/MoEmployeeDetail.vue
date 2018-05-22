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
      uuid: {type: String, required: true},
      detail: {type: String, required: true},
      columns: Array,
      entryComponent: Object,
      createLabel: String
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
    watch: {
      uuid () {
        this.getAllDetails()
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
