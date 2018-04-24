<template>
  <b-modal 
    id="employeeMoveMany" 
    size="lg" 
    title="Flyt mange engagementer"
    ref="employeeMoveMany"
    hide-footer 
    lazy
    no-close-on-backdrop
    @hidden="resetData"
  >
    <form @submit.stop.prevent="moveMany">
      <div class="form-row">
        <mo-date-picker 
          class="col" 
          label="Dato for flytning" 
          v-model="moveDate" 
          required
        />

        <mo-organisation-unit-picker 
          :is-disabled="dateSelected" 
          label="Flyttes fra" 
          v-model="orgUnitSource" 
          class="col" 
          required
        />
        
        <mo-organisation-unit-picker 
          :is-disabled="dateSelected" 
          label="Flyttes til" 
          v-model="orgUnitDestination" 
          class="col"
          required
        />       
      </div>

      <mo-table 
        v-if="sourceSelected"
        :content="employees" 
        :columns="columns"
        type="EMPLOYEE"
        multi-select 
        @selected-changed="selectedEmployees"
      />

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
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
    $_veeValidate: {
      validator: 'new'
    },
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
        columns: [
          {label: 'person', data: 'person'},
          {label: 'engagement_type', data: 'engagement_type'},
          {label: 'job_function', data: 'job_function'}
        ]
      }
    },
    computed: {
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      },

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
    methods: {
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },
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

      moveMany (evt) {
        evt.preventDefault()
        if (this.formValid) {
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
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
