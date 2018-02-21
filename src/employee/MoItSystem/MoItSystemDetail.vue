<template>
  <div>
    <mo-table-collapsible-tense
      :columns="columns"
      :content="details"
      content-type="it"
      :loading="loading"
      :uuid="uuid"
      :edit-component="entryComponent"
    />

    <mo-entry-modal-base 
      type="CREATE" 
      :uuid="uuid" 
      label="Nyt IT system" 
      :entry-component="entryComponent"
      content-type="it"
    />
  </div>
</template>

<script>
  import Employee from '../../api/Employee'
  import { EventBus } from '../../EventBus'
  import MoTableCollapsibleTense from '../../components/MoTableCollapsibleTense'
  import MoEntryModalBase from '../../components/MoEntryModalBase'
  import MoItSystemEntry from './MoItSystemEntry'

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
        columns: ['it_system', 'user'],
        entryComponent: MoItSystemEntry
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
        Employee.getItDetails(this.uuid, tense)
        .then(response => {
          vm.loading[tense] = false
          vm.details[tense] = response
        })
      }
    }
  }
</script>
