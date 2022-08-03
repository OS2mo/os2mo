SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <b-modal
    id="orgUnitRename"
    ref="orgUnitRename"
    size="lg"
    :title="$t('workflows.organisation.rename_unit')"
    @hidden="resetData"
    hide-footer
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="renameOrganisationUnit">
      <div class="form-row">
        <mo-input-date
          class="from-date"
          :label="$t('input_fields.start_date')"
          v-model="rename.data.validity.from"
        />
        <mo-organisation-unit-picker
          :label="$t('input_fields.select_unit')"
          class="col"
          v-model="original"
          required
          :validity="validity"
        />
      </div>

      <div class="form-row">
        <mo-input-text
          v-model="rename.data.name"
          :label="$t('input_fields.new_name')"
          required
        />
      </div>
      <div class="alert alert-danger" v-if="compareName">
        {{ $t("alerts.error.COMPARE_ORG_RENAME_NAMES") }}
      </div>
      <div class="alert alert-danger" v-if="backendValidationMessage">
        {{ backendValidationMessage }}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading" />
      </div>
    </form>
  </b-modal>
</template>

<script>
/**
 * A organisation unit rename component.
 */

import OrganisationUnit from "@/api/OrganisationUnit"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import { MoInputText, MoInputDate } from "@/components/MoInput"
import ButtonSubmit from "@/components/ButtonSubmit"
import ValidateForm from "@/mixins/ValidateForm"
import ModalBase from "@/mixins/ModalBase"
import { mapGetters } from "vuex"
import { OrganisationUnit as OrgUnit } from "@/store/actions/organisationUnit"
import MoEntryBase from "@/components/MoEntry/MoEntryBase"
import moment from "moment"

export default {
  extends: MoEntryBase,

  mixins: [ValidateForm, ModalBase],

  components: {
    MoInputDate,
    MoOrganisationUnitPicker,
    MoInputText,
    ButtonSubmit,
  },

  data() {
    return {
      /**
       * The rename, original, isLoading component value.
       * Used to detect changes and restore the value.
       */
      original: this.orgUnit,
      rename: {
        type: "org_unit",
        data: {
          name: "",
          uuid: "",
          clamp: true,
          validity: {
            from: moment(new Date()).format("YYYY-MM-DD"),
          },
        },
      },
      isLoading: false,
      backendValidationMessage: null,
    }
  },

  computed: {
    /**
     * Get organisation unit
     */
    ...mapGetters({
      orgUnit: OrgUnit.getters.GET_ORG_UNIT,
    }),

    /**
     * Compare if the unit names are identical.
     * If then return false.
     */
    compareName() {
      if (this.rename.data.name && this.original.name) {
        if (this.original.name == null) return true
        if (this.rename.data.name === this.original.name) return true
      }
      return false
    },

    validity() {
      return {
        // Validation is meant to check an instant in time,
        // which is why 'to' is duplicated
        from: this.rename.data.validity.to,
        to: this.rename.data.validity.to,
      }
    },
  },

  watch: {
    /**
     * Whenever orgUnit changes, this function will run.
     */
    orgUnit: {
      handler(val) {
        this.original = val
        if (val) {
          this.rename.data.uuid = val.uuid
        }
      },
      deep: true,
    },
    original(val) {
      this.rename.data.uuid = val && val.uuid
    },
  },

  mounted() {
    /**
     * After the entire view has been rendered.
     * Set original to orgUnit.
     */
    this.original = this.orgUnit

    this.backendValidationMessage = null
  },

  methods: {
    /**
     * Resets the data fields name and validity.
     */
    resetData() {
      this.rename.data.name = ""
      this.rename.data.uuid = this.original && this.original.uuid
      this.rename.data.validity.from = moment(new Date()).format("YYYY-MM-DD")
      this.backendValidationMessage = null
    },

    /**
     * Rename a organisation unit and check if the data fields are valid.
     * Then throw a error if not.
     */
    renameOrganisationUnit(evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        vm.isLoading = true

        if (vm.compareName) {
          vm.isLoading = false
          return false
        }
        OrganisationUnit.rename(this.rename).then(this.handle.bind(this))
      } else {
        this.$validator.validateAll()
      }
    },

    handle(response) {
      this.isLoading = false
      if (response.error) {
        this.backendValidationMessage = this.$t(
          "alerts.error." + response.error_key,
          response
        )

        if (!this.backendValidationMessage) {
          this.backendValidationMessage = this.$t("alerts.fallback", response)
        }
      } else {
        this.backendValidationMessage = null
        this.$refs.orgUnitRename.hide()
        this.$store.commit("log/newWorkLog", {
          type: "ORGANISATION_RENAME",
          value: { original_name: this.original.name, new_name: this.rename.data.name },
        })
      }
    },
  },
}
</script>
