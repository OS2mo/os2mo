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
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'
import EmployeeDetailTabs from '@/employee/EmployeeDetailTabs'

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoEmployeePicker,
    MoDatePicker,
    ButtonSubmit,
    EmployeeDetailTabs
  },

  computed: {
    /**
       * Get mapFields from vuex store.
       */
    ...mapFields('employeeTerminate', [
      'employee',
      'endDate',
      'isLoading',
      'backendValidationError'
    ]),

    /**
       * Get mapGetters from vuex store.
       */
    ...mapGetters({
      details: 'employeeTerminate/getDetails'
    })
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
      let vm = this
      if (this.formValid) {
        this.$store.dispatch(`employeeTerminate/terminateEmployee`)
          .then(() => {
            vm.$refs.employeeTerminate.hide()
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
