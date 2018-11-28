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

export default {
  /**
       * Requesting a new validator scope to its children.
       */
  $_veeValidate: {
    validator: 'new'
  },

  components: {
    MoEmployeePicker,
    MoLeaveEntry,
    ButtonSubmit
  },

  data () {
    return {
      /**
        * The isLoading component value.
        * Used to detect changes and restore the value.
        */
      isLoading: false
    }
  },

  computed: {
    /**
       * Get mapFields from vuex store.
       */
    ...mapFields('employeeLeave', [
      'employee',
      'leave',
      'backendValidationError'
    ]),

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
    /**
       * Create leave and check if the data fields are valid.
       * Then throw a error if not.
       */
    createLeave () {
      if (this.formValid) {
        let vm = this
        vm.isLoading = true
        this.$store.dispatch('employeeLeave/LEAVE_EMPLOYEE')
          .then(response => {
            vm.isLoading = false
            if (response.error) {
              vm.backendValidationError = response.error_key
            } else {
              vm.$refs.employeeLeave.hide()
            }
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
