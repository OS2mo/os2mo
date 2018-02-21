<template>
  <div>
    <mo-table-collapsible-tense
      :columns="columns"
      :content="details"
      content-type="role"
      :loading="loading"
      :edit-component="entryComponent"
      :uuid="uuid"
    />

    <mo-entry-modal-base 
      type="CREATE" 
      :uuid="uuid" 
      label="Ny rolle" 
      :entry-component="entryComponent"
      content-type="role"
    />
  </div>
</template>


<script>
  import Employee from '../../api/Employee'
  import { EventBus } from '../../EventBus'
  import MoTableCollapsibleTense from '../../components/MoTableCollapsibleTense'
  import MoEntryModalBase from '../../components/MoEntryModalBase'
  import MoRoleEntry from './MoRoleEntry'

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
        columns: ['org_unit', 'role_type'],
        entryComponent: MoRoleEntry
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
        Employee.getRoleDetails(this.uuid, tense)
        .then(response => {
          vm.loading[tense] = false
          vm.details[tense] = response
        })
      }
    }
  }
</script>
