<template>
  <div>
    <mo-table-collapsible-tense
      :columns="columns"
      :content="details"
      :loading="loading"
      :edit-component="editComponent"
      :uuid="uuid"
    />

    <mo-engagement-modal :uuid="uuid" type="CREATE" label="Nyt engagement"/>
  </div>
</template>


<script>
  import Employee from '../../api/Employee'
  import { EventBus } from '../../EventBus'
  import MoTableCollapsibleTense from '../../components/MoTableCollapsibleTense'
  import MoEngagementModal from './MoEngagementModal'

  export default {
    components: {
      MoTableCollapsibleTense,
      MoEngagementModal
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
        editComponent: MoEngagementModal
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
