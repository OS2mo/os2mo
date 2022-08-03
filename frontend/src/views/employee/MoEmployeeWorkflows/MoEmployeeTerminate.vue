SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <form @submit.stop.prevent="terminateEmployee">
    <div class="form-row">
      <mo-input-date
        v-model="endDate"
        :label="$t('input_fields.end_date')"
        class="from-date"
        required
      />

      <mo-employee-picker
        v-model="employee"
        class="col search-employee"
        required
        :validity="validity"
      />
    </div>

    <div class="mb-3" v-if="employee">
      <p>{{ $t("workflows.employee.messages.following_will_be_terminated") }}</p>
      <employee-detail-tabs
        :uuid="employee.uuid"
        :content="details"
        @show="loadContent($event)"
        hide-actions
      />

      <mo-confirm-checkbox
        v-model="confirmCheckbox"
        :entry-date="endDate"
        :employee-name="employee.name"
        v-if="employee.name && endDate"
        required
      />
    </div>

    <div class="alert alert-danger" v-if="backendValidationError">
      {{
        $t("alerts.error." + backendValidationError.error_key, backendValidationError)
      }}
    </div>

    <div class="float-right">
      <button-submit :is-loading="isLoading" :disabled="isDisabled" />
    </div>
  </form>
</template>

<script>
/**
 * A employee terminate component.
 */

import { mapFields } from "vuex-map-fields"
import { mapGetters } from "vuex"
import MoEmployeePicker from "@/components/MoPicker/MoEmployeePicker"
import { MoInputDate } from "@/components/MoInput"
import ButtonSubmit from "@/components/ButtonSubmit"
import ValidateForm from "@/mixins/ValidateForm"
import MoConfirmCheckbox from "@/components/MoConfirmCheckbox"
import EmployeeDetailTabs from "../EmployeeDetailTabs"
import store from "./_store/employeeTerminate.js"

const STORE_KEY = "$_employeeTerminate"

export default {
  mixins: [ValidateForm],

  components: {
    MoEmployeePicker,
    MoInputDate,
    ButtonSubmit,
    EmployeeDetailTabs,
    MoConfirmCheckbox,
  },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      confirmCheckbox: true,
    }
  },

  computed: {
    /**
     * Get mapFields from vuex store.
     */
    ...mapFields(STORE_KEY, [
      "employee",
      "endDate",
      "isLoading",
      "backendValidationError",
    ]),

    /**
     * Get mapGetters from vuex store.
     */
    ...mapGetters({
      details: `${STORE_KEY}/getDetails`,
    }),

    isDisabled() {
      if (this.formValid && this.confirmCheckbox) {
        return false
      }
      return true
    },

    validity() {
      return {
        from: this.endDate,
        to: this.endDate,
      }
    },
  },

  beforeCreate() {
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
  },
  beforeDestroy() {
    this.$store.unregisterModule(STORE_KEY)
  },

  watch: {
    show(val) {
      if (!val) {
        this.onHidden()
      }
    },
  },

  methods: {
    loadContent(event) {
      this.$store.dispatch(`${STORE_KEY}/setDetails`, event)
    },

    /**
     * Terminate employee and check if the data fields are valid.
     * Then throw a error if not.
     */
    terminateEmployee() {
      let vm = this
      if (this.formValid) {
        this.$store.dispatch(`${STORE_KEY}/terminateEmployee`).then(() => {
          vm.$emit("submitted")
        })
      } else {
        this.$validator.validateAll()
      }
    },

    onHidden() {
      this.$store.dispatch(`${STORE_KEY}/resetFields`)
    },
  },
}
</script>
