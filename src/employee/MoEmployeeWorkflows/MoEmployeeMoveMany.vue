<template>
  <b-modal 
    id="employeeMoveMany" 
    size="lg" 
    title="Flyt mange engagementer"
    ref="employeeMoveMany"
    hide-footer 
    lazy
  >
    <form @submit.prevent="moveMany">
      <div class="form-row">
        <mo-date-picker class="col" label="Dato for flytning" v-model="moveDate"/>

        <mo-organisation-unit-picker 
          :is-disabled="dateSelected" 
          label="Flyttes fra" 
          v-model="orgUnitSource" 
          class="col"/>
        
        <mo-organisation-unit-picker 
          :is-disabled="dateSelected" 
          label="Flyttes til" 
          v-model="orgUnitDestination" 
          class="col"/>       
      </div>

      <mo-table 
        v-if="sourceSelected"
        :content="employees" 
        :columns="columns"
        type="EMPLOYEE"
        multi-select 
        @selected-changed="selectedEmployees"/>

      <div class="float-right">
        <button-submit :is-disabled="isDisabled" :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import Employee from '@/api/Employee'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoTable from '@/components/MoTable/MoTable'
  import ButtonSubmit from '@/components/ButtonSubmit'

  export default {
    components: {
      MoDatePicker,
      MoOrganisationUnitPicker,
      MoTable,
      ButtonSubmit
    },
    data () {
      return {
        employees: [],
        selected: [],
        moveDate: null,
        orgUnitSource: {},
        orgUnitDestination: {},
        isLoading: false,
        columns: ['person', 'engagement_type', 'job_function']
      }
    },
    computed: {
      dateSelected () {
        return !this.moveDate
      },

      sourceSelected () {
        return this.orgUnitSource.uuid
      },

      isDisabled () {
        return !this.moveDate || !this.orgUnitSource.uuid || !this.orgUnitDestination.uuid || this.selected.length === 0
      }
    },
    watch: {
      orgUnitSource: {
        handler (newVal) {
          if (newVal.uuid) this.getEmployees(newVal.uuid)
        },
        deep: true
      }
    },
    mounted () {
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
      selectedEmployees (val) {
        this.selected = val
      },

      getEmployees (orgUnitUuid) {
        let vm = this
        OrganisationUnit.getDetail(orgUnitUuid, 'engagement')
          .then(response => {
            vm.employees = response
          })
      },

      moveMany () {
        let vm = this
        vm.isLoading = true

        vm.selected.forEach(engagement => {
          let move = {
            type: 'engagement',
            data: {
              validity: {}
            }
          }

          move.uuid = engagement.uuid
          move.data.org_unit = vm.orgUnitDestination
          move.data.validity.from = vm.moveDate

          let uuid = engagement.person.uuid
          let data = [move]

          Employee.move(uuid, data)
            .then(response => {
              vm.isLoading = false
              vm.$refs.employeeMoveMany.hide()
            })
        })
      }
    }
  }
</script>
