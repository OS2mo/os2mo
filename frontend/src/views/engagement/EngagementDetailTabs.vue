SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <b-tabs v-model="tabIndex" lazy>
      <b-tab
        @click="navigateToTab('#engagement')"
        href="#engagement"
        :title="$t('tabs.engagement.engagement')"
      >
        <mo-table-detail
          type="ENGAGEMENT"
          :uuid="uuid"
          :content="content['engagement']"
          content-type="engagement"
          :columns="engagement"
          @show="loadContent('engagement', $event)"
          :entry-component="!hideActions ? components.engagement : undefined"
          hide-create
        />
      </b-tab>

      <b-tab
        @click="navigateToTab('#adresser')"
        href="#adresser"
        :title="$t('tabs.engagement.addresses')"
      >
        <mo-table-detail
          type="ENGAGEMENT"
          :uuid="uuid"
          :content="content['address']"
          content-type="address"
          :columns="address"
          @show="loadContent('address', $event)"
          :entry-component="!hideActions ? components.address : undefined"
        />
      </b-tab>
      <b-tab
        @click="navigateToTab('#engagement_association')"
        href="#engagement_association"
        :title="$tc('tabs.engagement.engagement_association', 2)"
      >
        <mo-table-detail
          type="ENGAGEMENT"
          :uuid="uuid"
          :content="content['engagement_association']"
          content-type="engagement_association"
          :columns="engagement_association"
          @show="loadContent('engagement_association', $event)"
          :entry-component="
            !hideActions ? components.engagement_association : undefined
          "
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
/**
 * A engagement detail tabs component.
 */

import { mapGetters } from "vuex"
import {
  MoEngagementEntry,
  MoEmployeeAddressEntry,
  MoEngagementAssociationEntry,
} from "@/components/MoEntry"
import MoTableDetail from "@/components/MoTable/MoTableDetail"
import bTabs from "bootstrap-vue/es/components/tabs/tabs"
import bTab from "bootstrap-vue/es/components/tabs/tab"
import { AtDate } from "@/store/actions/atDate"
import { generate_extension_columns } from "../shared/engagement_tab"

export default {
  components: {
    MoTableDetail,
    "b-tabs": bTabs,
    "b-tab": bTab,
  },

  props: {
    /**
     * Defines a unique identifier.
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
      tabs: ["#engagement", "#adresser", "#engagement_association"],
      currentDetail: "engagement",
      _atDate: undefined,

      /**
       * The component values.
       * Used to detect changes and restore the value for columns.
       */
      address: [
        { label: "address_type", data: "address_type" },
        { label: "visibility", data: "visibility" },
        { label: "address", data: null },
      ],
      engagement_association: [
        { label: "org_unit", data: "org_unit" },
        { label: "engagement_association_type", data: "engagement_association_type" },
      ],

      /**
       * Used to add the components in the tabs.
       */
      components: {
        engagement: MoEngagementEntry,
        address: MoEmployeeAddressEntry,
        engagement_association: MoEngagementAssociationEntry,
      },
    }
  },

  computed: {
    engagement() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]

      let columns = [
        { label: "person", data: "person" },
        { label: "org_unit", data: "org_unit" },
        { label: "job_function", data: "job_function" },
        { label: "engagement_type", data: "engagement_type" },
      ]

      if (conf.show_primary_engagement) {
        columns.splice(2, 0, { label: "primary", data: "primary" })
      }

      let extension_labels = conf.extension_field_ui_labels.split(",")
      columns = columns.concat(generate_extension_columns(extension_labels))

      return columns
    },

    ...mapGetters({
      atDate: AtDate.getters.GET,
    }),
  },

  watch: {
    atDate(newVal) {
      this._atDate = newVal
      for (const validity of ["present", "past", "future"]) {
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
