<template>
  <b-modal 
    id="employeeMoveMany" 
    size="lg" 
    :title="$t('workflows.employee.move_many_engagements')"
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
          :label="$t('input_fields.move_date')"
          v-model="moveDate" 
          required
        />

        <mo-organisation-unit-picker
          :is-disabled="dateSelected" 
          :label="$t('input_fields.move_from')"
          v-model="orgUnitSource" 
          class="col from-unit" 
          required
        />
        
        <mo-organisation-unit-picker
          :is-disabled="dateSelected" 
          :label="$t('input_fields.move_to')"
          v-model="orgUnitDestination" 
          class="col to-unit"
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

      <input type="hidden"
        v-if="sourceSelected"
        v-model="selected.length"
        :name="nameId"
        v-validate="{min_value: 1}" 
        data-vv-as="Valg af engagementer"
      >

      <span v-show="errors.has(nameId)" class="text-danger">
        {{ errors.first(nameId) }}
      </span>

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
  /**
   * A employee move many component.
   */

  import OrganisationUnit from '@/api/OrganisationUnit'
  import Employee from '@/api/Employee'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoTable from '@/components/MoTable/MoTable'
  import ButtonSubmit from '@/components/ButtonSubmit'

  export default {
      /**
       * Requesting a new validator scope to its children.
       */
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
        /**
         * The employees, selected, moveDate, orgUnitSource, orgUnitDestination,
         * isLoading, backendValidationError, columns component value.
         * Used to detect changes and restore the value.
         */
        employees: [],
        selected: [],
        moveDate: null,
        orgUnitSource: null,
        orgUnitDestination: null,
        isLoading: false,
        backendValidationError: null,
        columns: [
          {label: 'person', data: 'person'},
          {label: 'engagement_type', data: 'engagement_type'},
          {label: 'job_function', data: 'job_function'}
        ]
      }
    },

    computed: {
      /**
       * Loop over all contents of the fields object and check if they exist and valid.
       */
      formValid () {
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      },

      /**
       * Set dateSelected to disable if moveDate is selected.
       */
      dateSelected () {
        return !this.moveDate
      },

      /**
       * When sourceSelected is selected, return orgUnitSource.
       */
      sourceSelected () {
        if (this.orgUnitSource) return this.orgUnitSource.uuid
      },

      /**
       * Get name `engagement-picker`.
       */
      nameId () {
        return 'engagement-picker-' + this._uid
      }
    },

    watch: {
      /**
       * Whenever orgUnitSource changes, get employees.
       */
      orgUnitSource: {
        handler (newVal) {
          if (newVal) this.getEmployees(newVal.uuid)
        },
        deep: true
      }
    },

    methods: {
      /**
       * Resets the data fields.
       */
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },
  
      /**
       * Selected employees.
       */
      selectedEmployees (val) {
        this.selected = val
      },

      /**
       * Get employees detail.
       */
      getEmployees (orgUnitUuid) {
        let vm = this
        OrganisationUnit.getDetail(orgUnitUuid, 'engagement')
          .then(response => {
            vm.employees = response
          })
      },

      /**
       * Move many employees and check if the data fields are valid.
       * Then throw a error if not.
       */
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
                if (response.error) {
                  vm.backendValidationError = response.error_key
                } else {
                  vm.$refs.employeeMoveMany.hide()
                }
              })
          })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
