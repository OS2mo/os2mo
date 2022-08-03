SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div
    class="input-group alert"
    :class="errors.has('confirm') ? 'alert-warning' : 'alert-success'"
  >
    <input
      class="mt-2 mr-1"
      data-vv-as="checkbox"
      :name="nameId"
      type="checkbox"
      v-validate="'required'"
      v-model="confirm"
    />

    <h6 v-if="engagementName" class="mt-1">
      {{ $t("alerts.error.CONFIRM_ENGAGEMENT_END_DATE", alertEngagementData) }}
    </h6>

    <h6 v-if="employeeName" class="mt-1">
      {{ $t("alerts.error.CONFIRM_EMPLOYEE_TERMINATE", alertEmployeeData) }}
    </h6>
  </div>
</template>

<script>
/**
 * A confirm checkbox component.
 */
import moment from "moment"

export default {
  name: "MoConfirmCheckbox",

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  props: {
    /**
     * Defines a entry date.
     */
    entryDate: [Date, String],

    /**
     * Defines a entry name.
     */
    engagementName: String,

    /**
     * Defines a entry name.
     */
    employeeName: String,

    /**
     * Defines a entry OrgName.
     */
    entryOrgName: String,
  },

  data() {
    return {
      /**
       * The confirm component value.
       * Used to detect changes and restore the value.
       */
      confirm: false,
    }
  },

  mounted() {
    /**
     * Called after the instance has been mounted.
     * When it change validate.
     */
    this.$validator.validate(this.nameId)
  },

  computed: {
    /**
     * Get default name.
     */
    nameId() {
      return "confirm"
    },

    alertEngagementData() {
      return {
        engagementName: this.engagementName,
        orgName: this.entryOrgName,
        endDate: moment(this.entryDate).subtract(1, "d").format("DD-MM-YYYY"),
      }
    },

    alertEmployeeData() {
      return {
        employeeName: this.employeeName,
        endDate: moment(this.entryDate).format("DD-MM-YYYY"),
      }
    },
  },

  watch: {
    /**
     * Whenever value change validate.
     */
    value() {
      this.confirm = false
      this.$validator.validate(this.nameId)
    },
  },
}
</script>
