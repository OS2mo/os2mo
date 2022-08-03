SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <label v-if="!noLabel">{{ label }}</label>

    <div class="input-group">
      <input
        :name="nameId"
        :data-vv-as="label"
        v-model.trim="cprNo"
        autocomplete="off"
        spellcheck="false"
        class="form-control"
        type="text"
      />
    </div>

    <mo-loader v-show="isLoading" />

    <div class="alert alert-danger" v-if="backendValidationError">
      {{
        $t("alerts.error." + backendValidationError.error_key, backendValidationError)
      }}
    </div>
  </div>
</template>

<script>
/**
 * cpr search component.
 */

import Search from "@/api/Search"
import MoLoader from "@/components/atoms/MoLoader"
import { mapGetters } from "vuex"
import { Organisation } from "@/store/actions/organisation"

export default {
  name: "MoCprSearch",

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: "$validator",
  },

  components: {
    MoLoader,
  },

  props: {
    /**
     * This boolean property defines a label if it does not have one.
     */
    noLabel: Boolean,

    /**
     * Defines a default label name.
     */
    label: { type: String, default: "CPR nummer" },

    /**
     * This boolean property requires a valid cpr number.
     */
    required: Boolean,
  },

  data() {
    return {
      /**
       * The nameId, cprNo, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
      nameId: "cpr-search",
      cprNo: "",
      isLoading: false,
      backendValidationError: null,
    }
  },

  watch: {
    /**
     * Whenever cprNo change look up cpr number and check if the data fields
     * are valid. Then throw a error if not.
     */
    async cprNo(cprNo) {
      if (cprNo.length < 10) {
        this.backendValidationError = cprNo ? { error_key: "V_CPR_NOT_VALID" } : null
        this.$emit("input", {})
        return
      }

      this.backendValidationError = null
      this.isLoading = true

      let response = await Search.cprLookup(cprNo && cprNo.replace(/-/g, ""))

      this.isLoading = false

      if (response.error) {
        this.backendValidationError = response
        this.$emit("input", {})
      } else {
        this.$emit("input", response)
      }
    },
  },

  computed: {
    /**
     * Get worklog message.
     */
    ...mapGetters({
      orgUuid: Organisation.getters.GET_UUID,
    }),
  },
}
</script>
