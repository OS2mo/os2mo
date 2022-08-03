SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <form @submit.stop.prevent="createLeave">
    <mo-leave-entry v-model="leave" />

    <mo-employee-picker
      v-model="leave.person"
      required
      :validity="leave.validity"
      :extra-validations="validations"
    />

    <div class="alert alert-danger" v-if="backendValidationError">
      {{
        $t("alerts.error." + backendValidationError.error_key, backendValidationError)
      }}
    </div>

    <div class="float-right">
      <button-submit :is-loading="isLoading" />
    </div>
  </form>
</template>

<script>
/**
 * A employee create leave component.
 */

import { mapFields } from "vuex-map-fields"
import MoEmployeePicker from "@/components/MoPicker/MoEmployeePicker"
import { MoLeaveEntry } from "@/components/MoEntry"
import ButtonSubmit from "@/components/ButtonSubmit"
import ValidateForm from "@/mixins/ValidateForm"
import store from "./_store/employeeLeave.js"

const STORE_KEY = "$_employeeLeave"

export default {
  mixins: [ValidateForm],

  components: {
    MoEmployeePicker,
    MoLeaveEntry,
    ButtonSubmit,
  },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    /**
     * Get mapFields from vuex store.
     */
    ...mapFields(STORE_KEY, [
      "employee",
      "leave",
      "isLoading",
      "backendValidationError",
    ]),

    validations() {
      return {
        active_engagements: [this.leave.validity],
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
    /**
     * Create leave and check if the data fields are valid.
     * Then throw a error if not.
     */
    createLeave() {
      let vm = this
      if (this.formValid) {
        this.$store.dispatch(`${STORE_KEY}/leaveEmployee`).then((response) => {
          if (response.error) {
            vm.backendValidationError = response
          } else {
            vm.$emit("submitted")
          }
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
