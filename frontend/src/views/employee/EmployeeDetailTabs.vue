SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <b-tabs v-model="tabIndex" lazy>
      <b-tab
        @click="navigateToTab('#medarbejder')"
        href="#medarbejder"
        :title="$t('tabs.employee.employee')"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['employee']"
          content-type="employee"
          :columns="employee"
          @show="loadContent('employee', $event)"
          :entry-component="!hideActions ? components.employee : undefined"
          hide-create
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#engagementer')"
        href="#engagementer"
        :title="$t('tabs.employee.engagements')"
      >
        <mo-table-detail
          v-if="engagement !== undefined"
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['engagement']"
          content-type="engagement"
          :columns="engagement"
          @show="loadContent('engagement', $event)"
          :entry-component="!hideActions ? components.engagement : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#adresser')"
        href="#adresser"
        :title="$t('tabs.employee.addresses')"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['address']"
          content-type="address"
          :columns="address"
          @show="loadContent('address', $event)"
          :entry-component="!hideActions ? components.address : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#roller')"
        href="#roller"
        :title="$t('tabs.employee.roles')"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['role']"
          content-type="role"
          :columns="role"
          @show="loadContent('role', $event)"
          :entry-component="!hideActions ? components.role : undefined"
        />
      </b-tab>

      <b-tab @click="navigateToTab('#it')" href="#it" :title="$t('tabs.employee.it')">
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['it']"
          content-type="it"
          :columns="it"
          @show="loadContent('it', $event)"
          :entry-component="!hideActions ? components.it : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#tilknytninger')"
        href="#tilknytninger"
        :title="$tc('tabs.employee.association', 2)"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['association']"
          content-type="association"
          :columns="association"
          @show="loadContent('association', $event)"
          :entry-component="!hideActions ? components.association : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#ittilknytninger')"
        href="#ittilknytninger"
        :title="$tc('tabs.employee.itassociation', 2)"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['itassociation']"
          content-type="association"
          :columns="itassociation"
          @show="loadContent('itassociation', $event)"
          :entry-component="!hideActions ? components.itassociation : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#orlov')"
        href="#orlov"
        :title="$t('tabs.employee.leave')"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['leave']"
          content-type="leave"
          :columns="leave"
          @show="loadContent('leave', $event)"
          :entry-component="!hideActions ? components.leave : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#leder')"
        href="#leder"
        :title="$t('tabs.employee.manager')"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['manager']"
          content-type="manager"
          :columns="manager"
          @show="loadContent('manager', $event)"
          :entry-component="!hideActions ? components.manager : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#owner')"
        href="#owner"
        :title="$t('tabs.employee.owner')"
        v-if="show_owner"
      >
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['owner']"
          content-type="owner"
          :columns="owner"
          @show="loadContent('owner', $event)"
          :entry-component="!hideActions ? components.owner : undefined"
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
/**
 * A employee detail tabs component.
 */

import { mapGetters } from "vuex"
import {
  MoEmployeeEntry,
  MoEngagementEntry,
  MoEmployeeAddressEntry,
  MoRoleEntry,
  MoItSystemEntry,
  MoAssociationEntry,
  MoItAssociationEntry,
  MoLeaveEntry,
  MoManagerEntry,
  MoOwnerEntry,
} from "@/components/MoEntry"
import MoTableDetail from "@/components/MoTable/MoTableDetail"
import bTabs from "bootstrap-vue/es/components/tabs/tabs"
import bTab from "bootstrap-vue/es/components/tabs/tab"
import { Facet } from "@/store/actions/facet"
import { AtDate } from "@/store/actions/atDate"
import { Conf } from "@/store/actions/conf"
import { columns, generate_extension_columns } from "../shared/engagement_tab"

export default {
  components: {
    MoTableDetail,
    "b-tabs": bTabs,
    "b-tab": bTab,
  },

  props: {
    /**
     * Defines a unique identifier which must be unique.
     */
    uuid: String,

    content: Object,

    /**
     * This Boolean property hides the actions.
     */
    hideActions: Boolean,
  },

  data() {
    return {
      tabIndex: 0,
      tabs: [
        "#medarbejder",
        "#engagementer",
        "#adresser",
        "#roller",
        "#it",
        "#tilknytninger",
        "#ittilknytninger",
        "#orlov",
        "#leder",
        "#owner",
      ],
      currentDetail: "employee",
      _atDate: undefined,
      /**
       * The leave, it, address, engagement, association, role, manager component value.
       * Used to detect changes and restore the value for columns.
       */
      role: [
        { label: "org_unit", data: "org_unit" },
        { label: "role_type", data: "role_type" },
      ],
      it: [
        { label: "it_system", data: "itsystem" },
        { label: "user_key", data: null, field: "user_key" },
        { label: "primary", data: "primary", field: "user_key" },
      ],
      leave: [
        { label: "leave_type", data: "leave_type" },
        { label: "engagement", field: null, data: "engagement" },
      ],
      manager: [
        { label: "org_unit", data: "org_unit" },
        { label: "responsibility", data: "responsibility" },
        { label: "manager_type", data: "manager_type" },
        { label: "manager_level", data: "manager_level" },
      ],
      owner: [
        { label: "owner", data: "owner" },
        {
          label: "owner_inference_priority",
          data: "owner_inference_priority",
          field: null,
        },
      ],
      address: [
        { label: "address_type", data: "address_type" },
        { label: "visibility", data: "visibility" },
        { label: "address", data: null },
      ],
      itassociation: [
        { label: "org_unit", data: "org_unit" },
        { label: "job_function", data: "job_function" },
        { label: "it_system", data: "it", field: "itsystem" },
        { label: "user_key", data: "it", field: "user_key" },
        { label: "primary", data: "primary", field: "user_key" },
      ],

      /**
       * The MoEngagementEntry, MoAddressEntry, MoRoleEntry, MoItSystemEntry,
       * MoAssociationEntry, MoLeaveEntry, MoManagerEntry component.
       * Used to add the components in the tabs.
       */
      components: {
        employee: MoEmployeeEntry,
        engagement: MoEngagementEntry,
        address: MoEmployeeAddressEntry,
        role: MoRoleEntry,
        it: MoItSystemEntry,
        association: MoAssociationEntry,
        itassociation: MoItAssociationEntry,
        leave: MoLeaveEntry,
        manager: MoManagerEntry,
        owner: MoOwnerEntry,
      },
    }
  },

  computed: {
    employee() {
      let cols = [
        { label: "name", data: "name", field: null },
        { label: "nickname", data: "nickname", field: null },
      ]
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      if (conf.show_seniority) {
        cols.push({ label: "seniority", data: "seniority", field: null })
      }
      return cols
    },

    engagement() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]

      if (!("extension_field_ui_labels" in conf)) {
        return undefined
      }

      let dyn_columns = [{ label: "org_unit", data: "org_unit" }]
      dyn_columns = dyn_columns.concat(columns)
      if (conf.show_primary_engagement) {
        dyn_columns.push({ label: "primary", data: "primary" })
      }

      let extension_labels = conf.extension_field_ui_labels.split(",")
      dyn_columns = dyn_columns.concat(generate_extension_columns(extension_labels))
      return dyn_columns
    },

    association() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      let facet_getter = this.$store.getters[Facet.getters.GET_FACET]
      let columns = [
        { label: "org_unit", data: "org_unit" },
        { label: "first_party_association_type", data: "first_party_association_type" },
        { label: "third_party_associated", data: "third_party_associated" },
        { label: "third_party_association_type", data: "third_party_association_type" },
      ]

      if (conf.association_dynamic_facets) {
        let dynamics = conf.association_dynamic_facets
          .split(",")
          .filter((elem) => elem != "")
        // Function called to determine header label
        let label_function_generator = function (uuid) {
          return function () {
            return facet_getter(uuid)["description"]
          }
        }
        for (const dynamic of dynamics) {
          this.$store.dispatch(Facet.actions.SET_FACET, { facet: dynamic, full: true })
          columns.push({
            label: "dynamic_class",
            label_function: label_function_generator(dynamic),
            data: dynamic,
          })
        }
      }

      if (conf.show_primary_association) {
        columns.splice(1, 0, { label: "primary", data: "primary" })
      }

      return columns
    },

    show_owner() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      return conf.show_owner
    },

    show_it_associations() {
      let conf = this.$store.getters[Conf.getters.GET_CONF_DB]
      return conf.show_it_associations_tab
    },

    ...mapGetters({
      atDate: AtDate.getters.GET,
    }),
  },

  watch: {
    atDate(newVal) {
      this._atDate = newVal
      for (var validity of ["present", "past", "future"]) {
        this.loadContent(this.currentDetail, validity)
      }
    },
  },

  created() {
    this._atDate = this.$store.getters[AtDate.getters.GET]
  },

  mounted() {
    this.tabIndex = this.tabs.findIndex((tab) => tab == this.$route.hash)
  },

  methods: {
    loadContent(contentType, event) {
      let payload = {
        uuid: this.uuid,
        detail: contentType,
        validity: event,
        atDate: this._atDate,
        extra: {},
      }
      if (contentType === "association") {
        payload.extra.first_party_perspective = "1"
      }
      this.currentDetail = contentType
      this.$emit("show", payload)
    },

    navigateToTab(tabTarget) {
      this.$router.replace(tabTarget)
    },
  },
}
</script>
