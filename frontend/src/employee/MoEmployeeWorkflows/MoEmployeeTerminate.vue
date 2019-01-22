<template>
  <form @submit.stop.prevent="terminateEmployee">
    <div class="form-row">
      <mo-employee-picker
        v-model="employee"
        class="col search-employee"
        required
      />

      <mo-input-date
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
</template>

<script>
/**
 * A employee terminate component.
 */

import { mapFields } from 'vuex-map-fields'
import { mapGetters } from 'vuex'
import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
import { MoInputDate } from '@/components/MoInput'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import EmployeeDetailTabs from '@/employee/EmployeeDetailTabs'
import store from './_store/employeeTerminate.js'

const STORE_KEY = '$_employeeTerminate'

export default {
  mixins: [ValidateForm],

  components: {
    MoEmployeePicker,
    MoInputDate,
    ButtonSubmit,
    EmployeeDetailTabs
  },
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },

  computed: {
    /**
     * Get mapFields from vuex store.
     */
    ...mapFields(STORE_KEY, [
      'employee',
      'endDate',
      'isLoading',
      'backendValidationError'
    ]),

    /**
     * Get mapGetters from vuex store.
     */
    ...mapGetters({
      details: `${STORE_KEY}/getDetails`
    })
  },
  beforeCreate () {
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
  },
  beforeDestroy () {
    this.$store.unregisterModule(STORE_KEY)
  },

  watch: {
    show (val) {
      if (!val) {
        this.onHidden()
      }
    }
  },

  methods: {
    loadContent (event) {
      this.$store.dispatch(`${STORE_KEY}/setDetails`, event)
    },

    /**
     * Terminate employee and check if the data fields are valid.
     * Then throw a error if not.
     */
    terminateEmployee () {
      let vm = this
      if (this.formValid) {
        this.$store.dispatch(`${STORE_KEY}/terminateEmployee`)
          .then(() => {
            vm.$emit('submitted')
          })
      } else {
        this.$validator.validateAll()
      }
    },

    onHidden () {
      this.$store.dispatch(`${STORE_KEY}/resetFields`)
    }
  }
}
</script>
