SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <form @submit.stop.prevent="createEmployee">
    <mo-cpr v-if="enableCPR" v-model="employee" />

    <div class="form-row name">
      <label>{{ $t("shared.name") }}</label>
      <mo-input-text
        :placeholder="$t('input_fields.givenname')"
        v-model="employee.name"
        :disabled="disableManualName"
      />
    </div>

    <div class="form-row nickname">
      <label>{{ $t("shared.nickname") }}</label>
      <mo-input-text
        :placeholder="$t('input_fields.givenname')"
        v-model="employee.nickname_givenname"
      />
      <mo-input-text
        :placeholder="$t('input_fields.surname')"
        v-model="employee.nickname_surname"
      />
    </div>

    <mo-input-date
      :label="$t('shared.seniority')"
      v-model="employee.seniority"
      v-bind:clear-button="true"
      v-if="show_seniority"
    />

    <mo-add-many
      class="btn-engagement mt-3"
      v-model="engagement"
      :entry-component="entry.engagement"
      :label="$tc('workflows.employee.labels.engagement', 2)"
    />

    <mo-add-many
      class="btn-address mt-3"
      v-model="address"
      :entry-component="entry.address"
      :label="$tc('workflows.employee.labels.address', 2)"
      validity-hidden
    />

    <mo-add-many
      class="btn-association mt-3"
      v-model="association"
      :entry-component="entry.association"
      :label="$tc('workflows.employee.labels.association', 2)"
      validity-hidden
    />

    <mo-add-many
      class="btn-role mt-3"
      v-model="role"
      :entry-component="entry.role"
      :label="$tc('workflows.employee.labels.role', 2)"
      validity-hidden
    />

    <mo-add-many
      class="btn-itSystem mt-3"
      v-model="itSystem"
      :entry-component="entry.it"
      :label="$tc('workflows.employee.labels.it_system', 2)"
      validity-hidden
    />

    <mo-add-many
      class="btn-manager mt-3"
      v-model="manager"
      :entry-component="entry.manager"
      :label="$tc('workflows.employee.labels.manager')"
      validity-hidden
    />

    <mo-add-many
      v-if="show_owner"
      class="btn-manager mt-3"
      v-model="owner"
      :entry-component="entry.owner"
      :label="$tc('workflows.employee.labels.owner')"
      validity-hidden
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
 * A employee create component.
 */

import { mapFields } from "vuex-map-fields"
import ButtonSubmit from "@/components/ButtonSubmit"
import MoCpr from "@/components/MoCpr"
import { MoInputText, MoInputDate } from "@/components/MoInput"
import MoAddMany from "@/components/MoAddMany/MoAddMany"
import ValidateForm from "@/mixins/ValidateForm"
import {
  MoEmployeeAddressEntry,
  MoAssociationEntry,
  MoEngagementEntry,
  MoRoleEntry,
  MoItSystemEntry,
  MoManagerEntry,
  MoOwnerEntry,
} from "@/components/MoEntry"
import store from "./_store/employeeCreate.js"

const STORE_KEY = "$_employeeCreate"

export default {
  mixins: [ValidateForm],

  components: {
    ButtonSubmit,
    MoCpr,
    MoInputText,
    MoInputDate,
    MoAddMany,
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

      /**
       * The entry - address, association, role, it, manager component.
       * Used to add MoAddressEntry, MoAssociationEntry, MoRoleEntry,
       * MoItSystemEntry, MoManagerEntry component in `<mo-add-many/>`.
       */
      entry: {
        engagement: MoEngagementEntry,
        address: MoEmployeeAddressEntry,
        association: MoAssociationEntry,
        role: MoRoleEntry,
        it: MoItSystemEntry,
        manager: MoManagerEntry,
        owner: MoOwnerEntry,
      },
    }
  },

  computed: {
    /**
     * Get mapFields from vuex store.
     */
    ...mapFields(STORE_KEY, [
      "employee",
      "engagement",
      "address",
      "association",
      "role",
      "itSystem",
      "manager",
      "owner",
      "organisation",
      "backendValidationError",
    ]),

    disableManualName() {
      // disable when using cpr (as cpr implies a name)
      return this.employee && "cpr_no" in this.employee
    },

    enableCPR() {
      // Keep enabled if name is disabled.
      // Otherwise, disable if we have a non-empty name.
      return (
        this.disableManualName ||
        !("name" in this.employee) ||
        ("name" in this.employee &&
          (this.employee.name === "" || this.employee.name == null))
      )
    },

    show_seniority() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      return conf.show_seniority
    },
    show_owner() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      return conf.show_owner
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
     * Create a employee and check if the data fields are valid.
     * Then throw a error if not.
     */
    updateOrganisation() {
      this.organisation = this.$store.getters["organisation/GET_ORGANISATION"]
    },

    createEmployee(evt) {
      this.updateOrganisation()
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        this.isLoading = true

        this.$store.dispatch(`${STORE_KEY}/CREATE_EMPLOYEE`).then((employeeUuid) => {
          vm.isLoading = false
          if (employeeUuid.error) {
            vm.backendValidationError = employeeUuid
          } else {
            vm.$emit("submitted")
            vm.$router.push({ name: "EmployeeDetail", params: { uuid: employeeUuid } })
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
