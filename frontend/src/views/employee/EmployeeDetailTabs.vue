SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <b-tabs v-model="tabIndex" lazy>
      <b-tab @click="navigateToTab('#engagementer')" href="#engagementer" :title="$t('tabs.employee.engagements')">
        <mo-table-detail
          type="EMPLOYEE"
          :uuid="uuid"
          :content="content['engagement'] "
          content-type="engagement"
          :columns="engagement"
          @show="loadContent('engagement', $event)"
          :entry-component="!hideActions ? components.engagement : undefined"
        />
      </b-tab>

      <b-tab @click="navigateToTab('#adresser')" href="#adresser" :title="$t('tabs.employee.addresses')">
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

      <b-tab @click="navigateToTab('#roller')" href="#roller" :title="$t('tabs.employee.roles')">
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

      <b-tab @click="navigateToTab('#tilknytninger')" href="#tilknytninger" :title="$tc('tabs.employee.association', 2)">
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

      <b-tab @click="navigateToTab('#orlov')" href="#orlov" :title="$t('tabs.employee.leave')">
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

      <b-tab @click="navigateToTab('#leder')" href="#leder" :title="$t('tabs.employee.manager')">
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
    </b-tabs>
  </div>
</template>

<script>
/**
 * A employee detail tabs component.
 */

import { MoEngagementEntry, MoEmployeeAddressEntry, MoRoleEntry, MoItSystemEntry, MoAssociationEntry, MoLeaveEntry, MoManagerEntry } from '@/components/MoEntry'
import MoTableDetail from '@/components/MoTable/MoTableDetail'
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
    uuid: String,

    content: Object,

    /**
     * This Boolean property hides the actions.
     */
    hideActions: Boolean
  },

  data () {
    return {
      tabIndex: 0,
      tabs: ['#engagementer', '#adresser', '#roller', '#it', '#tilknytninger', '#orlov', '#leder'],
      /**
       * The leave, it, address, engagement, association, role, manager component value.
       * Used to detect changes and restore the value for columns.
       */
      role: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'role_type', data: 'role_type' }
      ],
      it: [
        { label: 'it_system', data: 'itsystem' },
        { label: 'user_key', data: null, field: 'user_key' }
      ],
      leave: [
        { label: 'leave_type', data: 'leave_type' },
        { label: 'engagement', field: null, data: 'engagement' }
      ],
      manager: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'responsibility', data: 'responsibility' },
        { label: 'manager_type', data: 'manager_type' },
        { label: 'manager_level', data: 'manager_level' }
      ],
      address: [
        { label: 'address_type', data: 'address_type' },
        { label: 'visibility', data: 'visibility' },
        { label: 'address', data: null }
      ],

      /**
       * The MoEngagementEntry, MoAddressEntry, MoRoleEntry, MoItSystemEntry,
       * MoAssociationEntry, MoLeaveEntry, MoManagerEntry component.
       * Used to add the components in the tabs.
       */
      components: {
        engagement: MoEngagementEntry,
        address: MoEmployeeAddressEntry,
        role: MoRoleEntry,
        it: MoItSystemEntry,
        association: MoAssociationEntry,
        leave: MoLeaveEntry,
        manager: MoManagerEntry
      }
    }
  },

  computed: {
    engagement () {
      let conf = this.$store.getters['conf/GET_CONF_DB']

      let columns = [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'engagement_id', data: 'user_key', field: null },
        { label: 'job_function', data: 'job_function' },
        { label: 'engagement_type', data: 'engagement_type' }
      ]

      if (conf.show_primary_engagement) {
        columns.splice(2, 0,
          { label: 'primary', data: 'primary' }
        )
      }

      return columns
    },
    association () {
      let conf = this.$store.getters['conf/GET_CONF_DB']

      let columns = [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'association_type', data: 'association_type' }
      ]

      if (conf.show_primary_association) {
        columns.splice(1, 0,
          { label: 'primary', data: 'primary' }
        )
      }

      return columns
    }
  },

  mounted () {
    this.tabIndex = this.tabs.findIndex(tab => tab == this.$route.hash)
  },

  methods: {
    loadContent (contentType, event) {
      let payload = {
        detail: contentType,
        validity: event,
        uuid: this.uuid
      }
      this.$emit('show', payload)
    },
    navigateToTab (tabTarget) {
      this.$router.replace(tabTarget)
    }
  }
}
</script>
