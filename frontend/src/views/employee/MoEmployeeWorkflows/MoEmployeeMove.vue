SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <form @submit.stop.prevent="moveEmployee">
    <div class="form-row">
      <mo-input-date
        class="col from-date"
        :label="$t('input_fields.move_date')"
        v-model="from"
        required
      />
    </div>

    <mo-employee-picker
      class="search-employee"
      v-model="person"
      required
      :validity="validity"
    />

    <div class="form-row">
      <mo-engagement-picker
        class="mt-3"
        v-model="original"
        :employee="person"
        required
      />
    </div>

    <div class="form-row">
      <mo-organisation-unit-picker
        :label="$t('input_fields.move_to')"
        class="col"
        v-model="org_unit"
        required
        :validity="validity"
      />
    </div>

    <mo-confirm-checkbox
      :entry-date="from"
      :engagement-name="original.engagement_type.name"
      :entry-org-name="original.org_unit.name"
      v-if="dateConflict"
      required
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
 * A employee move component.
 */

import { MoInputDate } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoEngagementPicker from "@/components/MoPicker/MoEngagementPicker"
import MoEmployeePicker from "@/components/MoPicker/MoEmployeePicker"
import ButtonSubmit from "@/components/ButtonSubmit"
import MoConfirmCheckbox from "@/components/MoConfirmCheckbox"
import ValidateForm from "@/mixins/ValidateForm"
import { mapFields } from "vuex-map-fields"
import store from "./_store/employeeMove.js"

const STORE_KEY = "$_employeeMove"

export default {
  mixins: [ValidateForm],

  components: {
    MoInputDate,
    MoOrganisationUnitPicker,
    MoEngagementPicker,
    MoEmployeePicker,
    ButtonSubmit,
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
      /**
       * The isLoading component value.
       * Used to detect changes and restore the value.
       */
      isLoading: false,
    }
  },

  computed: {
    /**
     * Get mapFields from vuex store.
     */
    ...mapFields(STORE_KEY, [
      "move",
      "move.data.person",
      "move.data.org_unit",
      "move.data.validity.from",
      "original",
      "backendValidationError",
    ]),

    /**
     * Check if the dates are valid.
     */
    dateConflict() {
      if (this.from && this.original) {
        if (this.original.validity.to == null) return true
        const newFrom = new Date(this.from)
        const originalTo = new Date(this.original.validity.to)
        if (newFrom <= originalTo) return true
      }
      return false
    },

    validity() {
      return {
        from: this.from,
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
     * Move a employee and check if the data fields are valid.
     * Then throw a error if not.
     */
    moveEmployee(evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        vm.isLoading = true

        this.$store.dispatch(`${STORE_KEY}/MOVE_EMPLOYEE`).then((response) => {
          vm.isLoading = false
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
