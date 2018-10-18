<template>
  <b-modal 
    id="employeeTerminate" 
    size="lg" 
    :title="$t('workflows.employee.terminate_employee')"
    ref="employeeTerminate"
    @hidden="$store.dispatch('employeeTerminate/resetFields')"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="terminateEmployee">
      <div class="form-row">
        <mo-employee-picker 
          v-model="employee" 
          class="col search-employee" 
          required
        />

        <mo-date-picker 
          v-model="endDate" 
          :label="$t('input_fields.end_date')" 
          class="from-date" 
          required
        />
      </div>

      <div class="mb-3" v-if="employee.uuid">
        <p>{{$t('workflows.employee.messages.following_will_be_terminated')}}</p>
        <employee-detail-tabs 
          :uuid="employee.uuid"
          :content="details" 
          @show="loadContent($event)"
          hide-actions
        />
      </div>

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
   * A employee terminate component.
   */

  import { mapFields } from 'vuex-map-fields'
  import { mapGetters } from 'vuex'
  import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import EmployeeDetailTabs from '@/employee/EmployeeDetailTabs'

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
      EmployeeDetailTabs
    },

    data () {
      return {
        isLoading: false,
        backendValidationError: null
      }
    },

    computed: {
      ...mapFields('employeeTerminate', [
        'employee',
        'endDate'
      ]),

      ...mapGetters({
        details: 'employeeTerminate/getDetails'
      }),

      /**
       * Check validity of form. this.fields is a magic property created by vee-validate
       */
      formValid () {
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      }
    },

    methods: {

      loadContent (event) {
        this.$store.dispatch('employeeTerminate/setDetails', event)
      },

      /**
       * Terminate employee and check if the data fields are valid.
       * Then throw a error if not.
       */
      terminateEmployee () {
        if (this.formValid) {
          let vm = this
          vm.isLoading = true
          this.$store.dispatch('employeeTerminate/TERMINATE_EMPLOYEE')
            .then(response => {
              vm.isLoading = false
              if (response.error) {
                vm.backendValidationError = response.error_key
              } else {
                vm.$refs.employeeTerminate.hide()
              }
            })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
