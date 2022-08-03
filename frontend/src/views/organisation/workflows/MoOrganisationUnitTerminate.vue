SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <b-modal
    id="orgUnitTerminate"
    ref="orgUnitTerminate"
    size="lg"
    :title="$t('workflows.organisation.terminate_unit')"
    @hidden="onHidden"
    hide-footer
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="endOrganisationUnit">
      <div class="form-row">
        <mo-input-date
          class="from-date"
          :label="$t('input_fields.end_date')"
          v-model="terminate.validity.to"
          required
        />

        <mo-organisation-unit-picker
          :label="$t('input_fields.select_unit')"
          class="col"
          v-model="org_unit"
          required
          :validity="validity"
        />
      </div>

      <div class="mb-3" v-if="org_unit && org_unit.uuid">
        <p>{{ $t("workflows.organisation.messages.following_will_be_terminated") }}</p>
        <organisation-detail-tabs
          :uuid="org_unit.uuid"
          :org-unit-info="org_unit"
          :content="orgUnitDetails"
          @show="loadContent($event)"
          timemachine-friendly
        />
      </div>

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
 * A organisation unit terminate component.
 */

import OrganisationUnit from "@/api/OrganisationUnit"
import { MoInputDate } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import ButtonSubmit from "@/components/ButtonSubmit"
import OrganisationDetailTabs from "@/views/organisation/OrganisationDetailTabs"
import ValidateForm from "@/mixins/ValidateForm"
import ModalBase from "@/mixins/ModalBase"
import { mapGetters } from "vuex"
import orgUnitStore from "@/store/modules/organisationUnit"
import moment from "moment"

const STORE_KEY = "_organisationUnitTerminate"

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoInputDate,
    MoOrganisationUnitPicker,
    ButtonSubmit,
    OrganisationDetailTabs,
  },

  data() {
    return {
      /**
       * The terminate, org_unit, isLoading, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
      org_unit: null,
      terminate: {
        validity: {
          to: moment(new Date()).format("YYYY-MM-DD"),
        },
      },
      isLoading: false,
      backendValidationError: null,
    }
  },

  computed: {
    ...mapGetters({
      orgUnitDetails: STORE_KEY + "/GET_DETAILS",
    }),

    validity() {
      return {
        // Validation is meant to check an instant in time,
        // which is why 'to' is duplicated
        from: this.terminate.validity.to,
        to: this.terminate.validity.to,
      }
    },
  },

  created() {
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, orgUnitStore)
    }
  },

  watch: {
    org_unit(val) {
      if (val) {
        this.$store.dispatch(STORE_KEY + "/SET_ORG_UNIT", val.uuid)
      } else {
        this.$store.commit(STORE_KEY + "/RESET_ORG_UNIT")
      }
    },
  },

  methods: {
    onHidden() {
      Object.assign(this.$data, this.$options.data())
      this.org_unit = null
    },

    loadContent(event) {
      event.atDate = this.terminate.from || new Date()
      this.latestEvent = event
      this.$store.dispatch(STORE_KEY + "/SET_DETAIL", event)
    },

    /**
     * Terminate a organisation unit and check if the data fields are valid.
     * Then throw a error if not.
     */
    endOrganisationUnit(evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        vm.isLoading = true
        OrganisationUnit.terminate(
          this.org_unit.uuid,
          this.terminate,
          this.org_unit.name
        ).then((response) => {
          vm.isLoading = false
          if (response.error) {
            vm.backendValidationError = response
          } else {
            vm.$refs.orgUnitTerminate.hide()
          }
        })
      } else {
        this.$validator.validateAll()
      }
    },
  },
}
</script>
