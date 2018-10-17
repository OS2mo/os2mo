<template>
  <b-modal 
    id="employeeLeave" 
    size="lg" 
    :title="$t('workflows.employee.leave')"
    ref="employeeLeave"
    hide-footer 
    lazy
    no-close-on-backdrop
    @hidden="resetData"
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

  import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
  import MoLeaveEntry from '@/components/MoEntry/MoLeaveEntry'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import { LEAVE_EMPLOYEE, SET_EMPLOYEE, GET_EMPLOYEE, SET_LEAVE, GET_LEAVE } from '@/vuex/actions/employeeLeave'

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
        * The isLoading, backendValidationError component value.
        * Used to detect changes and restore the value.
        */
        isLoading: false,
        backendValidationError: null
      }
    },

    computed: {
      /**
       * Get and set a employee.
       */
      employee: {
        get () { return this.$store.getters['employeeLeave/' + GET_EMPLOYEE] },
        set (value) { this.$store.commit('employeeLeave/' + SET_EMPLOYEE, value) }
      },

      /**
       * Get and set leave data.
       */
      leave: {
        get () { return this.$store.getters['employeeLeave/' + GET_LEAVE] },
        set (value) { this.$store.commit('employeeLeave/' + SET_LEAVE, value) }
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

    watch: {
      /**
       * Called whenever the selected person changes
       */
      employee: {
        handler (newVal) {
          this.leave.person = newVal
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
        this.$store.commit('employeeLeave/' + SET_EMPLOYEE, {})
      },

      /**
       * Create leave and check if the data fields are valid.
       * Then throw a error if not.
       */
      createLeave (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true
          this.$store.dispatch('employeeLeave/' + LEAVE_EMPLOYEE)
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
