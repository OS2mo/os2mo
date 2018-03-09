<template>
  <b-modal 
    id="employeeMoveMany" 
    size="lg" 
    hide-footer 
    title="Flyt mange engagementer"
    ref="employeeMoveMany"
    lazy
  >
    <div class="form-row">
      <date-picker 
        class="col"
        label="Dato for flytning"
        v-model="moveDate"
      />

      <organisation-unit-picker :is-disabled="dateSelected" label="Flyttes fra" v-model="orgUnitSource" class="col"/>
      
      <organisation-unit-picker :is-disabled="dateSelected" label="Flyttes til" v-model="orgUnitDestination" class="col"/>       
    </div>

    <mo-table 
      v-if="sourceSelected"
      :content="employees" 
      :columns="columns"
      type="EMPLOYEE"
      multi-select 
      @selected-changed="selectedEmployees"/>

    <div class="float-right">
      <button-submit :is-disabled="isDisabled" :is-loading="isLoading" :on-click-action="moveMany"/>
    </div>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '../../api/OrganisationUnit'
  import Employee from '../../api/Employee'
  import DatePicker from '../../components/DatePicker'
  import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
  import MoTable from '../../components/MoTable'
  import ButtonSubmit from '../../components/ButtonSubmit'

  export default {
    components: {
      DatePicker,
      OrganisationUnitPicker,
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
          this.getEmployees(newVal.uuid)
        },
        deep: true
      }
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

        let move = {
          type: 'engagement',
          data: {
            validity: {}
          }
        }

        vm.selected.forEach(engagement => {
          move.uuid = engagement.uuid
          move.data.org_unit = vm.orgUnitDestination
          move.data.validity.from = vm.moveDate

          Employee.edit(engagement.person.uuid, [move])
            .then(response => {
              vm.isLoading = false
              vm.$refs.employeeMoveMany.hide()
            })
        })
      }
    }
  }
</script>
