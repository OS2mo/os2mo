<template>
  <b-modal 
    id="employeeTerminate" 
    size="lg" 
    :title="$t('workflows.employee.terminate_employee')"
    ref="employeeTerminate"
    @hidden="resetData"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="endEmployee">
      <div class="form-row">
        <mo-employee-picker 
          class="col search-employee" 
          v-model="employee" 
          required
        />

        <mo-date-picker 
          class="from-date" 
          :label="$t('input_fields.end_date')" 
          v-model="terminate.validity.to" 
          required
        />
      </div>
        
        <div class="mb-3" v-if="employee">
          <p>Følgende vil blive afsluttet for medarbejderen:</p>
          <mo-employee-detail-tabs :uuid="employee.uuid" hide-actions/>
        </div>

        <div class="float-right">
          <button-submit :is-loading="isLoading"/>
        </div>
    </form>
  </b-modal>
</template>

<script>
  /**
   * A employee terminate component.
   */

  import Employee from '@/api/Employee'
  import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import MoEmployeeDetailTabs from '@/employee/EmployeeDetailTabs'

  export default {
      /**
       * Requesting a new validator scope to its children.
       */
    $_veeValidate: {
      validator: 'new'
    },

    components: {
      MoEmployeePicker,
      MoDatePicker,
      ButtonSubmit,
      MoEmployeeDetailTabs
    },

    data () {
      return {
        /**
         * The terminate, employee, isLoading component value.
         * Used to detect changes and restore the value.
         */
        isLoading: false,
        employee: null,
        terminate: {
          validity: {}
        }
      }
    },

    computed: {
      isDisabled () {
        return !this.employee.uuid || !this.terminate.validity.to
      },

      /**
       * Loop over all contents of the fields object and check if they exist and valid.
       */
      formValid () {
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
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
       * Terminate employee and check if the data fields are valid.
       * Then throw a error if not.
       */
      endEmployee (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true
          Employee.terminate(this.employee.uuid, this.terminate)
            .then(response => {
              vm.isLoading = false
              vm.$refs.employeeTerminate.hide()
            })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
