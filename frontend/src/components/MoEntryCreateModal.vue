SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div v-if="hasEntryComponent">
    <button class="btn btn-outline-primary" v-b-modal="nameId">
      <icon name="plus" />
      {{ $t("buttons.create_new") }}
    </button>

    <b-modal
      :id="nameId"
      size="lg"
      hide-footer
      :title="$t('common.create')"
      :ref="nameId"
      lazy
    >
      <mo-input-date-range v-model="validity" :disabled-dates="{ disabledDates }" />

      <form @submit.stop.prevent="create">
        <mo-add-many
          class="btn-address mt-3"
          v-model="entries"
          :entry-component="entryComponent"
          :label="$tc('shared.add_more', 2)"
          :hide-org-picker="hideOrgPicker"
          :hide-employee-picker="hideEmployeePicker"
          validity-hidden
        />

        <div class="alert alert-danger" v-if="backendValidationError">
          {{
            $t(
              "alerts.error." + backendValidationError.error_key,
              backendValidationError
            )
          }}
        </div>

        <div class="float-right">
          <button-submit :is-loading="isLoading" />
        </div>
      </form>
    </b-modal>
  </div>
</template>

<script>
/**
 * A entry create modal component.
 */

import Employee from "@/api/Employee"
import OrganisationUnit from "@/api/OrganisationUnit"
import ButtonSubmit from "@/components/ButtonSubmit"
import ValidateForm from "@/mixins/ValidateForm"
import ModalBase from "@/mixins/ModalBase"
import bModalDirective from "bootstrap-vue/es/directives/modal/modal"
import MoAddMany from "@/components/MoAddMany/MoAddMany"
import { MoInputDateRange } from "@/components/MoInput"
import Engagement from "@/api/Engagement"

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    ButtonSubmit,
    MoInputDateRange,
    MoAddMany,
  },
  directives: {
    "b-modal": bModalDirective,
  },

  props: {
    /**
     * Defines a uuid.
     */
    uuid: String,

    /**
     * Defines a entryComponent.
     */
    entryComponent: Object,

    /**
     * Defines a required type - employee or organisation unit.
     */
    type: {
      type: String,
      required: true,
      validator(value) {
        if (value === "EMPLOYEE" || value === "ORG_UNIT" || value === "ENGAGEMENT")
          return true
        console.warn("Action must be either EMPLOYEE or ORG_UNIT or ENGAGEMENT")
        return false
      },
    },
  },

  data() {
    return {
      /**
       * The entry, isLoading, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
      entries: [{}],
      subject: {},
      validity: {},
      isLoading: false,
      backendValidationError: null,
    }
  },

  computed: {
    /**
     * Get name `moCreate`.
     */
    nameId() {
      return "moCreate" + this._uid
    },

    /**
     * If it has a entry component.
     */
    hasEntryComponent() {
      return this.entryComponent !== undefined
    },

    /**
     * Get hideOrgPicker type.
     */
    hideOrgPicker() {
      return this.type === "ORG_UNIT"
    },

    /**
     * Get hideEmployeePicker type.
     */
    hideEmployeePicker() {
      return this.type === "EMPLOYEE"
    },

    disabledDates() {
      if (this.type === "ORG_UNIT") {
        return this.subject.validity
      }
    },
  },

  mounted() {
    /**
     * Whenever it changes, reset data.
     */
    this.$root.$on("bv::modal::hidden", () => {
      Object.assign(this.$data, this.$options.data())
    })

    switch (this.type) {
      case "EMPLOYEE":
        this.subject = { uuid: this.uuid }
        break
      case "ORG_UNIT":
        this.subject = this.$store.getters["organisationUnit/GET_ORG_UNIT"]
        break
    }
  },

  beforeDestroy() {
    /**
     * Called right before a instance is destroyed.
     */
    this.$root.$off(["bv::modal::hidden"])
  },

  watch: {
    entries: {
      deep: true,
      handler: function (val) {
        if (this.type === "EMPLOYEE") {
          val.forEach((entry) => {
            if (!entry.person) {
              entry.person = { uuid: this.uuid }
            }
          })
        }
      },
    },
  },

  methods: {
    /**
     * Create a employee or organisation entry.
     */
    create() {
      if (!this.formValid) {
        this.$validator.validateAll()
        return
      }

      this.entries.forEach((entry) => {
        entry.org = this.$store.getters["organisation/GET_ORGANISATION"]
        if (!entry.validity) {
          entry.validity = this.validity
        }
      })

      this.isLoading = true

      switch (this.type) {
        case "EMPLOYEE":
          this.entries.forEach((entry) => {
            entry.person = { uuid: this.uuid }
          })
          this.createEmployeeEntries(this.entries)
          break
        case "ORG_UNIT":
          this.entries.forEach((entry) => {
            entry.org_unit = { uuid: this.uuid }
          })
          this.createOrganisationUnitEntries(this.entries)
          break
        case "ENGAGEMENT":
          this.entries.forEach((entry) => {
            entry.engagement = { uuid: this.uuid }
          })
          this.createEngagementEntries(this.entries)
          break
      }
    },

    /**
     * Create a list of entries for an employee
     * Then throw a error if not.
     */
    createEmployeeEntries(data) {
      let vm = this
      Employee.create(data).then((response) => {
        vm.isLoading = false
        if (response.error) {
          vm.backendValidationError = response
        } else {
          vm.$refs[this.nameId].hide()
          this.$emit("submit")
          for (const dat of data) {
            this.$store.commit(
              "log/newWorkLog",
              {
                type: "FUNCTION_CREATE",
                contentType: this.contentType,
                value: { type: this.$tc(`shared.${dat.type}`, 1) },
              },
              { root: true }
            )
          }
        }
      })
    },

    /**
     * Create list of entries for an organisational unit
     * Then throw a error if not.
     */
    createOrganisationUnitEntries(data) {
      let vm = this
      return OrganisationUnit.createEntry(data).then((response) => {
        vm.isLoading = false
        if (response.error) {
          vm.backendValidationError = response
        } else {
          vm.$refs[this.nameId].hide()
          this.$emit("submit")
          for (const dat of data) {
            this.$store.commit(
              "log/newWorkLog",
              {
                type: "FUNCTION_CREATE",
                contentType: this.contentType,
                value: { type: this.$tc(`shared.${dat.type}`, 1) },
              },
              { root: true }
            )
          }
        }
      })
    },

    /**
     * Create list of entries for an organisational function
     * Then throw a error if not.
     */
    createEngagementEntries(data) {
      let vm = this
      return Engagement.createEntry(data).then((response) => {
        vm.isLoading = false
        if (response.error) {
          vm.backendValidationError = response
        } else {
          vm.$refs[this.nameId].hide()
          this.$emit("submit")
          for (const dat of data) {
            this.$store.commit(
              "log/newWorkLog",
              {
                type: "FUNCTION_CREATE",
                contentType: this.contentType,
                value: { type: this.$tc(`shared.${dat.type}`, 1) },
              },
              { root: true }
            )
          }
        }
      })
    },
  },
}
</script>
