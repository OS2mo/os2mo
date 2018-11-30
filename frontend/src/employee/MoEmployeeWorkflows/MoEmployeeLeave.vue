<template>
  <b-modal
    id="employeeLeave"
    size="lg"
    :title="$t('workflows.employee.leave')"
    ref="employeeLeave"
    hide-footer
    lazy
    no-close-on-backdrop
    @hidden="$store.dispatch('employeeLeave/resetFields')"
  >
    <form @submit.stop.prevent="createLeave">
      <mo-employee-picker v-model="employee" required/>

      <mo-leave-entry class="mt-3" v-model="leave"/>

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
   * A employee create leave component.
   */

import { mapFields } from 'vuex-map-fields'
import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
import MoLeaveEntry from '@/components/MoEntry/MoLeaveEntry'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoEmployeePicker,
    MoLeaveEntry,
    ButtonSubmit
  },

  computed: {
    /**
       * Get mapFields from vuex store.
       */
    ...mapFields('employeeLeave', [
      'employee',
      'leave',
      'isLoading',
      'backendValidationError'
    ])
  },

  methods: {
    /**
       * Create leave and check if the data fields are valid.
       * Then throw a error if not.
       */
    createLeave () {
      let vm = this
      if (this.formValid) {
        this.$store.dispatch(`employeeLeave/leaveEmployee`)
          .then(() => {
            vm.$refs.employeeLeave.hide()
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
