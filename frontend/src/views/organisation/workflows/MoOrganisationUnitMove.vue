SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <b-modal
    id="orgUnitMove"
    ref="orgUnitMove"
    size="lg"
    :title="$t('workflows.organisation.move_unit')"
    @hidden="resetData"
    hide-footer
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="moveOrganisationUnit">
      <div class="form-row">
        <mo-input-date
          class="moveDate"
          :label="$t('input_fields.move_date')"
          v-model="move.data.validity.from"
          required
        />

        <div class="col">
          <mo-organisation-unit-picker
            class="currentUnit"
            v-model="original"
            :label="$t('input_fields.select_unit')"
            :validity="requiredValidity"
            :extra-validations="unitValidations"
            required
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group col">
          <label>{{ $t("input_fields.current_super_unit") }}</label>
          <input
            type="text"
            class="form-control"
            :value="original && original.parent && original.parent.name"
            disabled
          />
        </div>
      </div>

      <mo-organisation-unit-picker
        class="parentUnit"
        v-model="parent"
        :label="$t('input_fields.select_new_super_unit')"
        :validity="requiredValidity"
        :disabled-unit="original"
        :extra-validations="parentValidations"
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
  </b-modal>
</template>

<script>
/**
 * A organisation unit move component.
 */

import OrganisationUnit from "@/api/OrganisationUnit"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import { MoInputDate } from "@/components/MoInput"
import ButtonSubmit from "@/components/ButtonSubmit"
import ValidateForm from "@/mixins/ValidateForm"
import ModalBase from "@/mixins/ModalBase"
import { mapGetters } from "vuex"
import { OrganisationUnit as OrgUnit } from "@/store/actions/organisationUnit"
import moment from "moment"

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoOrganisationUnitPicker,
    MoInputDate,
    ButtonSubmit,
  },

  data() {
    return {
      /**
       * The move, parentUnit, uuid, original, isLoading, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
      original: this.orgUnit,
      parent: null,
      move: {
        type: "org_unit",
        data: {
          parent: {
            uuid: "",
          },
          uuid: "",
          clamp: true,
          validity: {
            from: moment(new Date()).format("YYYY-MM-DD"),
          },
        },
      },
      isLoading: false,
      backendValidationError: null,
    }
  },

  computed: {
    ...mapGetters({
      orgUnit: OrgUnit.getters.GET_ORG_UNIT,
    }),

    /**
     * A validity of one day, corresponding to the required validity
     * of units: They only need to be valid on the date of the operation.
     */
    requiredValidity() {
      return {
        from: this.move.data.validity.from,
        to: this.move.data.validity.from,
      }
    },

    parentValidations() {
      return {
        candidate_parent_org_unit: [
          this.original,
          this.move.data.parent,
          this.move.data.validity,
        ],
      }
    },
  },

  watch: {
    /**
     * If original exist show its parent.
     */
    "original.uuid"(newVal) {
      this.move.data.uuid = newVal
    },
    "parent.uuid"(newVal) {
      this.move.data.parent.uuid = newVal
    },
    orgUnit: {
      handler(val) {
        this.original = val
        if (val) {
          this.move.data.uuid = val.uuid
        }
      },
      deep: true,
    },
    original(val) {
      this.move.data.uuid = val && val.uuid
    },
  },

  mounted() {
    /**
     * After the entire view has been rendered.
     * Set original to orgUnit.
     */
    this.original = this.orgUnit
  },

  methods: {
    /**
     * Resets the data fields.
     */
    resetData() {
      this.move.data.validity.from = moment(new Date()).format("YYYY-MM-DD")
      this.move.data.uuid = this.original && this.original.uuid
      this.parent = null
      this.backendValidationError = null
    },

    /**
     * Move a organisation unit and check if the data fields are valid.
     * Then throw a error if not.
     */
    moveOrganisationUnit(evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        vm.isLoading = true
        OrganisationUnit.move(this.move, this.original.name, this.parent.name).then(
          (response) => {
            vm.isLoading = false
            if (response.error) {
              vm.backendValidationError = response
            } else {
              vm.$refs.orgUnitMove.hide()
            }
          }
        )
      } else {
        this.$validator.validateAll()
      }
    },
  },
}
</script>
