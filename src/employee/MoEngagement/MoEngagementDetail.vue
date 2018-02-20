<template>
  <div>
    <mo-collapse title="Fremtid">
      <mo-table 
        :columns="columns"
        :content="detailsFuture"
        :is-loading="loading.future"
        :edit-component="editComponent"
        :edit-uuid="uuid"
      />
    </mo-collapse>
    <mo-collapse title="Nutid" initially-open>
      <mo-table 
        :columns="columns"
        :content="details"
        :is-loading="loading.present"
        :edit-component="editComponent"
        :edit-uuid="uuid"
      />
    </mo-collapse>

    <mo-collapse title="Fortid">
      <mo-table 
        :columns="columns"
        :content="detailsPast"
        :is-loading="loading.past"
        :edit-component="editComponent"
        :edit-uuid="uuid"
      />
    </mo-collapse>

    <mo-engagement-modal :uuid="uuid" type="CREATE" label="Nyt engagement"/>
  </div>
</template>


<script>
  import Employee from '../../api/Employee'
  import '../../filters/GetProperty'
  import { EventBus } from '../../EventBus'
  import MoCollapse from '../../components/MoCollapse'
  import MoTable from '../../components/MoTable'
  import Loading from '../../components/Loading'
  import MoEngagementModal from './MoEngagementModal'

  export default {
    components: {
      MoCollapse,
      MoTable,
      Loading,
      MoEngagementModal
    },
    props: {
      value: Object,
      uuid: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        details: [],
        detailsPast: [],
        detailsFuture: [],
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
        this.getDetails()
        this.getDetailsPast()
        this.getDetailsFuture()
      },

      getDetails () {
        let vm = this
        vm.loading.present = true
        Employee.getEngagementDetails(this.uuid)
        .then(response => {
          vm.loading.present = false
          vm.details = response
        })
      },

      getDetailsPast () {
        let vm = this
        vm.loading.past = true
        Employee.getEngagementDetails(this.uuid, 'past')
        .then(response => {
          vm.loading.past = false
          vm.detailsPast = response
        })
      },

      getDetailsFuture () {
        let vm = this
        vm.loading.future = true
        Employee.getEngagementDetails(this.uuid, 'future')
        .then(response => {
          vm.loading.future = false
          vm.detailsFuture = response
        })
      }
    }
  }
</script>
<style scoped>

th{
  background-color: #ffffff;
}

</style>
