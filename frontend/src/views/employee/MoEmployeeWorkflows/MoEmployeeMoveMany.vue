SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <form @submit.stop.prevent="moveMany">
    <div class="form-row">
      <mo-input-date
        class="col"
        :label="$t('input_fields.move_date')"
        v-model="moveDate"
        required
      />

      <mo-organisation-unit-picker
        :is-disabled="dateSelected"
        :label="$t('input_fields.move_from')"
        v-model="orgUnitSource"
        class="col from-unit"
        required
        :validity="validity"
      />

      <mo-organisation-unit-picker
        :is-disabled="dateSelected"
        :label="$t('input_fields.move_to')"
        v-model="orgUnitDestination"
        class="col to-unit"
        required
        :validity="validity"
      />
    </div>

    <mo-table
      v-model="selected"
      v-if="orgUnitSource"
      :content="employees"
      :columns="columns"
      type="EMPLOYEE"
      multi-select
    />

    <input
      type="hidden"
      v-if="orgUnitSource"
      name="selected-employees-count"
      :value="selected.length"
      v-validate="{ min_value: 1, required: true }"
    />

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
 * A employee move many component.
 */

import { MoInputDate } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoTable from "@/components/MoTable/MoTable"
import ButtonSubmit from "@/components/ButtonSubmit"
import ValidateForm from "@/mixins/ValidateForm"
import { mapFields } from "vuex-map-fields"
import { mapGetters } from "vuex"
import store from "./_store/employeeMoveMany.js"

const STORE_KEY = "$_employeeMoveMany"

export default {
  mixins: [ValidateForm],

  components: {
    MoInputDate,
    MoOrganisationUnitPicker,
    MoTable,
    ButtonSubmit,
  },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isLoading: false,
      orgUnitSource: undefined,
    }
  },

  computed: {
    /**
     * generate getter/setters from store
     */
    ...mapFields(STORE_KEY, [
      "selected",
      "moveDate",
      "orgUnitDestination",
      "columns",
      "backendValidationError",
    ]),

    ...mapGetters(STORE_KEY, ["employees"]),

    /**
     * Set dateSelected to disabled if moveDate is selected.
     */
    dateSelected() {
      return !this.moveDate
    },

    isDisabled() {
      if (this.formValid && this.selected.length) {
        return false
      }
      return true
    },

    validity() {
      return { from: this.moveDate }
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
    /**
     * Whenever orgUnitSource changes, get employees.
     * @todo this could probably be improved. right now we need to reset orgUnitSource in the moveMany response.
     */
    orgUnitSource: {
      handler(newVal) {
        this.$store.commit(`${STORE_KEY}/updateOrgUnitSource`, newVal)
        this.$store.dispatch(`${STORE_KEY}/getEmployees`)
      },
      deep: true,
    },

    show(val) {
      if (!val) {
        this.onHidden()
      }
    },
  },

  methods: {
    /**
     * Check if fields are valid, and move employees if they are.
     * Otherwise validate the fields.
     */
    moveMany(evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        vm.isLoading = true

        this.$store.dispatch(`${STORE_KEY}/moveManyEmployees`).then((response) => {
          vm.isLoading = false
          if (response.error) {
            vm.backendValidationError = response
          } else {
            vm.orgUnitSource = undefined
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
