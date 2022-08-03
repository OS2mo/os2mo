SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div v-if="orgUnitInfo.user_settings.orgunit">
    <b-tabs v-model="tabIndex" lazy>
      <b-tab
        @click="navigateToTab('#org-unit')"
        href="#org-unit"
        :title="$t('tabs.organisation.unit')"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['org_unit']"
          content-type="org_unit"
          :columns="org_unit"
          @show="loadContent('org_unit', $event)"
          :entry-component="!timemachineFriendly ? components.orgUnit : undefined"
          hide-create
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#adresser')"
        href="#adresser"
        :title="$t('tabs.organisation.addresses')"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['address']"
          content-type="address"
          :columns="address"
          @show="loadContent('address', $event)"
          :entry-component="!timemachineFriendly ? components.address : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#engagementer')"
        href="#engagementer"
        :title="$t('tabs.organisation.engagements')"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['engagement']"
          content-type="engagement"
          :columns="engagement"
          @show="loadContent('engagement', $event)"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#tilknytninger')"
        href="#tilknytninger"
        :title="$tc('tabs.organisation.association', 2)"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['association']"
          content-type="association"
          :columns="association"
          @show="loadContent('association', $event)"
          :entry-component="timemachineFriendly ? undefined : components.association"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#it')"
        :href="'#it'"
        :title="$t('tabs.organisation.it')"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['it']"
          content-type="it"
          :columns="it"
          @show="loadContent('it', $event)"
          :entry-component="!timemachineFriendly ? components.itSystem : undefined"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#roller')"
        href="#roller"
        :title="$t('tabs.organisation.roles')"
        :disabled="!orgUnitInfo.user_settings.orgunit.show_roles"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['role']"
          content-type="role"
          :columns="role"
          @show="loadContent('role', $event)"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#ledere')"
        href="#ledere"
        :title="$t('tabs.organisation.managers')"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['manager']"
          content-type="manager"
          :columns="manager"
          @show="loadContent('manager', $event)"
          :entry-component="timemachineFriendly ? undefined : components.manager"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#kle')"
        href="#kle"
        :title="$t('tabs.organisation.kle')"
        :disabled="!orgUnitInfo.user_settings.orgunit.show_kle"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['kle']"
          content-type="kle"
          :columns="kle"
          @show="loadContent('kle', $event)"
          :entry-component="timemachineFriendly ? undefined : components.kle"
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#relateret')"
        href="#relateret"
        :title="$t('tabs.organisation.related')"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['related_unit']"
          content-type="related_unit"
          :columns="related_unit"
          @show="loadContent('related_unit', $event)"
        />
      </b-tab>
      <b-tab
        @click="navigateToTab('#owner')"
        href="#owner"
        :title="$t('tabs.organisation.owner')"
        v-if="show_owner"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['owner']"
          content-type="owner"
          :columns="owner"
          @show="loadContent('owner', $event)"
          :entry-component="timemachineFriendly ? undefined : components.owner"
        />
      </b-tab>
      <b-tab
        @click="navigateToTab('#engagement_association')"
        href="#engagement_association"
        :title="$t('tabs.organisation.engagement_association')"
        v-if="orgUnitInfo.user_settings.orgunit.show_engagement_hyperlink"
      >
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['engagement_association']"
          content-type="engagement_association"
          :columns="engagement_association"
          @show="loadContent('engagement_association', $event)"
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
/**
 * A organisation detail tabs component.
 */

import { mapGetters } from "vuex"
import MoTableDetail from "@/components/MoTable/MoTableDetail"
import {
  MoOrganisationUnitEntry,
  MoOrgUnitAddressEntry,
  MoItSystemEntry,
  MoManagerEntry,
  MoKLEEntry,
  MoAssociationEntry,
  MoEngagementAssociationEntry,
  MoOwnerEntry,
} from "@/components/MoEntry"
import bTabs from "bootstrap-vue/es/components/tabs/tabs"
import bTab from "bootstrap-vue/es/components/tabs/tab"
import { AtDate } from "@/store/actions/atDate"
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
    uuid: { type: String, required: true },
    orgUnitInfo: Object,
    content: Object,

    /**
     * This Boolean property indicates the timemachine output.
     */
    timemachineFriendly: Boolean,
  },

  data() {
    return {
      tabIndex: 0,
      tabs: [
        "#org-unit",
        "#adresser",
        "#engagementer",
        "#tilknytninger",
        "#it",
        "#roller",
        "#ledere",
        "#kle",
        "#relateret",
      ],
      // keep track of the latest tap shown
      latestTab: [],
      currentDetail: "org_unit",
      _atDate: undefined,
      /**
       * The address, engagement, association, role, manager component value.
       * Used to detect changes and restore the value for columns.
       */
      address: [
        { label: "address_type", data: "address_type" },
        { label: "visibility", data: "visibility" },
        { label: "address", data: null },
      ],
      role: [
        { label: "person", data: "person" },
        { label: "role_type", data: "role_type" },
      ],
      it: [
        { label: "it_system", data: "itsystem" },
        { label: "user_key", data: null, field: "user_key" },
      ],
      manager: [
        { label: "person", data: "person" },
        { label: "responsibility", data: "responsibility" },
        { label: "manager_type", data: "manager_type" },
        { label: "manager_level", data: "manager_level" },
      ],
      owner: [{ label: "owner", data: "owner" }],
      kle: [
        { label: "kle_aspect", data: "kle_aspect" },
        { label: "kle_number", data: "kle_number" },
      ],
      related_unit: [
        // NB: the backend always returns both units in a mapping,
        // ordered by uuid; one of these is always _this_ unit, but we
        // don't have an easy way to suppress that one, yet, so just
        // display both :(
        { label: "related_org_unit", data: "org_unit", index: 0 },
        { label: "related_org_unit", data: "org_unit", index: 1 },
      ],

      engagement_association: [
        { label: "engagement_id", data: "engagement", field: "user_key" },
        { label: "engagement_association_type", data: "engagement_association_type" },
      ],

      /**
       * The MoOrganisationUnitEntry, MoAddressEntry component.
       * Used to add edit and create for orgUnit and address.
       */
      components: {
        orgUnit: MoOrganisationUnitEntry,
        address: MoOrgUnitAddressEntry,
        itSystem: MoItSystemEntry,
        manager: MoManagerEntry,
        association: MoAssociationEntry,
        kle: MoKLEEntry,
        engagement_association: MoEngagementAssociationEntry,
        owner: MoOwnerEntry,
      },
    }
  },

  computed: {
    org_unit() {
      let columns = [
        { label: "org_unit", data: null },
        { label: "org_unit_type", data: "org_unit_type" },
        { label: "parent", data: "parent" },
      ]

      if (this.orgUnitInfo.user_settings.orgunit.show_time_planning) {
        columns.splice(2, 0, { label: "time_planning", data: "time_planning" })
      }

      if (this.orgUnitInfo.user_settings.orgunit.show_level) {
        columns.splice(2, 0, { label: "org_unit_level", data: "org_unit_level" })
      }

      return columns
    },

    engagement() {
      let dyn_columns = [{ label: "person", data: "person" }]

      if (this.orgUnitInfo.user_settings.orgunit.show_primary_engagement) {
        dyn_columns.push({ label: "primary", data: "primary" })
      }
      dyn_columns = dyn_columns.concat(columns)
      let extension_labels =
        this.orgUnitInfo.user_settings.orgunit.extension_field_ui_labels.split(",")
      dyn_columns = dyn_columns.concat(generate_extension_columns(extension_labels))
      return dyn_columns
    },

    association() {
      let columns = [
        { label: "person", data: "person" },
        { label: "association_type", data: "association_type" },
        { label: "substitute", data: "substitute" },
      ]

      if (this.orgUnitInfo.user_settings.orgunit.show_primary_association) {
        columns.splice(2, 0, { label: "primary", data: "primary" })
      }

      return columns
    },

    show_owner() {
      return this.orgUnitInfo.user_settings.orgunit.show_owner
    },

    ...mapGetters({
      atDate: AtDate.getters.GET,
    }),
  },

  watch: {
    /**
     * update content when uuid changes.
     * This part is needed for the timemachine, for some reason
     */
    uuid() {
      this.loadContent(this.latestTab.detail, this.latestTab.validity)
    },

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
    this.tabIndex = this.tabs.findIndex((tab) => tab === this.$route.hash)
  },

  methods: {
    loadContent(contentType, event) {
      let payload = {
        uuid: this.uuid,
        detail: contentType,
        validity: event,
        atDate: this._atDate,
      }
      this.latestTab = payload
      this.currentDetail = contentType
      this.$emit("show", payload)
    },

    navigateToTab(tabTarget) {
      this.$router.replace(tabTarget)
    },
  },
}
</script>
