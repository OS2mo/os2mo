SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div v-if="orgUnitInfo.user_settings.orgunit">
    <b-tabs v-model="tabIndex" lazy>
      <b-tab @click="navigateToTab('#org-unit')" href="#org-unit" :title="$t('tabs.organisation.unit')">
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

      <b-tab @click="navigateToTab('#adresser')" href="#adresser" :title="$t('tabs.organisation.addresses')">
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

      <b-tab @click="navigateToTab('#engagementer')" href="#engagementer" :title="$t('tabs.organisation.engagements')">
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['engagement']"
          content-type="engagement"
          :columns="engagement"
          @show="loadContent('engagement', $event)"
        />
      </b-tab>

      <b-tab @click="navigateToTab('#tilknytninger')" href="#tilknytninger" :title="$tc('tabs.organisation.association', 2)">
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['association']"
          content-type="association"
          :columns="association"
          @show="loadContent('association', $event)"
        />
      </b-tab>

      <b-tab @click="navigateToTab('#it')" :href="'#it'" :title="$t('tabs.organisation.it')">
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

      <b-tab @click="navigateToTab('#roller')" href="#roller" :title="$t('tabs.organisation.roles')" v-if="orgUnitInfo.user_settings.orgunit.show_roles">
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['role']"
          content-type="role"
          :columns="role"
          @show="loadContent('role', $event)"
        />
      </b-tab>

      <b-tab @click="navigateToTab('#ledere')" href="#ledere" :title="$t('tabs.organisation.managers')">
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

      <b-tab @click="navigateToTab('#relateret')" href="#relateret" :title="$t('tabs.organisation.related')">
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['related_unit']"
          content-type="related_unit"
          :columns="related_unit"
          @show="loadContent('related_unit', $event)"
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
/**
 * A organisation detail tabs component.
 */
import MoTableDetail from '@/components/MoTable/MoTableDetail'
import { MoOrganisationUnitEntry, MoOrgUnitAddressEntry, MoItSystemEntry, MoManagerEntry } from '@/components/MoEntry'
import bTabs from 'bootstrap-vue/es/components/tabs/tabs'
import bTab from 'bootstrap-vue/es/components/tabs/tab'

export default {
  components: {
    MoTableDetail,
    'b-tabs': bTabs,
    'b-tab': bTab
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
    timemachineFriendly: Boolean
  },

  data () {
    return {
      tabIndex: 0,
      tabs: ['#org-unit', '#adresser', '#engagementer', '#tilknytninger', '#it', '#roller', '#ledere', '#relateret'],
      // keep track of the latest tap shown
      latestTab: [],
      /**
       * The address, engagement, association, role, manager component value.
       * Used to detect changes and restore the value for columns.
       */
      address: [
        { label: 'address_type', data: 'address_type' },
        { label: 'visibility', data: 'visibility' },
        { label: 'address', data: null }
      ],
      role: [
        { label: 'person', data: 'person' },
        { label: 'role_type', data: 'role_type' }
      ],
      it: [
        { label: 'it_system', data: 'itsystem' },
        { label: 'user_key', data: null, field: 'user_key' }
      ],
      manager: [
        { label: 'person', data: 'person' },
        { label: 'responsibility', data: 'responsibility' },
        { label: 'manager_type', data: 'manager_type' },
        { label: 'manager_level', data: 'manager_level' }
      ],
      related_unit: [
        // NB: the backend always returns both units in a mapping,
        // ordered by uuid; one of these is always _this_ unit, but we
        // don't have an easy way to suppress that one, yet, so just
        // display both :(
        { label: 'related_org_unit', data: 'org_unit', index: 0 },
        { label: 'related_org_unit', data: 'org_unit', index: 1 }
      ],

      /**
       * The MoOrganisationUnitEntry, MoAddressEntry component.
       * Used to add edit and create for orgUnit and address.
       */
      components: {
        orgUnit: MoOrganisationUnitEntry,
        address: MoOrgUnitAddressEntry,
        itSystem: MoItSystemEntry,
        manager: MoManagerEntry
      }
    }
  },
  computed: {
    org_unit () {
      let columns = [
        { label: 'org_unit', data: null },
        { label: 'org_unit_type', data: 'org_unit_type' },
        { label: 'parent', data: 'parent' }
      ]

      if (this.orgUnitInfo.user_settings.orgunit.show_time_planning) {
        columns.splice(2, 0,
          { label: 'time_planning', data: 'time_planning' }
        )
      }

      if (this.orgUnitInfo.user_settings.orgunit.show_level) {
        columns.splice(2, 0,
          { label: 'org_unit_level', data: 'org_unit_level' }
        )
      }

      return columns
    },
    engagement () {
      let columns = [
        { label: 'person', data: 'person' },
        { label: 'job_function', data: 'job_function' },
        { label: 'engagement_type', data: 'engagement_type' }
      ]

      if (this.orgUnitInfo.user_settings.orgunit.show_primary_engagement) {
        columns.splice(1, 0,
          { label: 'primary', data: 'primary' }
        )
      }

      return columns
    },
    association () {
      let columns = [
        { label: 'person', data: 'person' },
        { label: 'association_type', data: 'association_type' }
      ]

      if (this.orgUnitInfo.user_settings.orgunit.show_primary_association) {
        columns.splice(2, 0,
          { label: 'primary', data: 'primary' }
        )
      }

      return columns
    }
  },
  watch: {
    /**
     * update content when uuid changes.
     * This part is needed for the timemachine, for some reason
     */
    uuid () {
      this.loadContent(this.latestTab.detail, this.latestTab.validity)
    }
  },

  mounted() {
    this.tabIndex = this.tabs.findIndex(tab => tab === this.$route.hash)
  },

  methods: {
    loadContent (contentType, event) {
      let payload = {
        detail: contentType,
        validity: event,
        uuid: this.uuid
      }
      this.latestTab = payload
      this.$emit('show', payload)
    },
    navigateToTab (tabTarget) {
      this.$router.replace(tabTarget)
    }
  }
}
</script>
