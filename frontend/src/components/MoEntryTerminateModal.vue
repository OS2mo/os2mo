SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <button class="btn btn-outline-danger" v-b-modal="nameId">
      <icon name="ban" />
    </button>

    <b-modal
      class="mo-terminate-entry-dialog"
      :id="nameId"
      ref="functionTerminate"
      size="md"
      :title="title"
      @hidden="onHidden"
      hide-footer
      lazy
      no-close-on-backdrop
    >
      <form @submit.stop.prevent="terminate">
        <mo-input-date
          v-if="showToDate"
          class="from-date"
          :label="$t('input_fields.end_date')"
          :valid-dates="validDates"
          v-model="validity.to"
          required
        />

        <div v-if="!showToDate">
          <p>
            {{ $t("workflows.organisation.messages.registration_will_be_terminated") }}
          </p>
          <dl>
            <dt>{{ $t("shared.date.start_date") }}:</dt>
            <dd>{{ content.validity.from || $t("shared.none") }}</dd>
          </dl>
          <dl>
            <dt>{{ $t("shared.date.end_date") }}:</dt>
            <dd>{{ content.validity.to || $t("shared.none") }}</dd>
          </dl>
        </div>

        <div class="alert alert-danger" v-if="backendValidationError">
          {{
            $t(
              "alerts.error." + backendValidationError.error_key,
              backendValidationError
            )
          }}
        </div>

        <div class="float-right">
          <button-submit :disabled="!formValid" :is-loading="isLoading" />
        </div>
      </form>
    </b-modal>
  </div>
</template>

<script>
/**
 * Terminate an entry, e.g. an association or engagement.
 */

import { EventBus, Events } from "@/EventBus"
import Service from "@/api/HttpCommon"
import { MoInputDate } from "@/components/MoInput"
import ButtonSubmit from "@/components/ButtonSubmit"
import ValidateForm from "@/mixins/ValidateForm"
import ModalBase from "@/mixins/ModalBase"
import bModalDirective from "bootstrap-vue/es/directives/modal/modal"

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoInputDate,
    ButtonSubmit,
  },

  directives: {
    "b-modal": bModalDirective,
  },

  props: {
    type: {
      type: String,
      required: true,
    },
    content: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      validity: {},
      backendValidationError: null,
      isLoading: false,
    }
  },

  computed: {
    title() {
      let terminate = this.$t("common.terminate")
      let type = this.$tc("shared." + this.type, 1).toLowerCase()

      return `${terminate} ${type}`
    },

    nameId() {
      return "moTerminate" + this._uid
    },

    payload() {
      return {
        type: this.type,
        uuid: this.content.uuid,
        validity: this.type == "org_unit" ? this.content.validity : this.validity,
      }
    },

    /**
     * Check if the organisation date are valid.
     */
    validDates() {
      return {
        from: this.content.validity.from,
        to: this.content.validity.to,
      }
    },

    showToDate() {
      return this.type != "org_unit"
    },
  },

  methods: {
    onHidden() {
      Object.assign(this.$data, this.$options.data())
    },

    /**
     * Terminate a organisation unit and check if the data fields are valid.
     * Then throw a error if not.
     */
    terminate(evt) {
      evt.preventDefault()
      if (this.formValid) {
        this.isLoading = true

        return Service.post("/details/terminate", this.payload)
          .then((response) => {
            this.isLoading = false
            this.$refs.functionTerminate.hide()
            this.$emit("submit")

            // Add entry to work log
            this.$store.commit(
              "log/newWorkLog",
              {
                type: "FUNCTION_TERMINATE",
                value: {
                  type: this.$tc(`shared.${this.type}`, 1),
                  name: this.getEntryName(),
                  from: this.payload.validity.from,
                  to: this.payload.validity.to,
                },
              },
              { root: true }
            )

            if (this.type === "org_unit") {
              // Navigate to parent of OU that was just terminated
              this.$router.push({
                name: "OrganisationDetail",
                params: { uuid: this.content.parent.uuid },
              })

              // Refresh org unit tree view
              this.$nextTick(() => {
                EventBus.$emit(Events.UPDATE_TREE_VIEW)
              })
            }
          })
          .catch((err) => {
            this.backendValidationError = err.response.data
            this.isLoading = false
          })
      } else {
        this.$validator.validateAll()
      }
    },

    getEntryName() {
      if (this.type === "org_unit") {
        return this.content.name
      } else {
        return this.content.person.name
      }
    },
  },
}
</script>

<style scoped>
dl,
p {
  margin: 0;
}

dl dt,
dl dd {
  display: inline-block;
  margin: 0;
  font-weight: normal;
}
</style>
