<template>
  <div>
    <b-tabs lazy>
      <b-tab :title="$t('tabs.employee.engagements')" active>
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

      <b-tab :title="$t('tabs.employee.addresses')">
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

      <b-tab :title="$t('tabs.employee.roles')">
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

      <b-tab :title="$t('tabs.employee.it')">
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

      <b-tab :title="$tc('tabs.employee.association', 2)">
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

      <b-tab :title="$t('tabs.employee.leave')">
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

      <b-tab :title="$t('tabs.employee.manager')">
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
      /**
       * The leave, it, address, engagement, association, role, manager component value.
       * Used to detect changes and restore the value for columns.
       */
      engagement: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'job_function', data: 'job_function' },
        { label: 'engagement_type', data: 'engagement_type' }
      ],
      role: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'role_type', data: 'role_type' }
      ],
      it: [
        { label: 'it_system', data: 'itsystem' },
        { label: 'user_key', data: null, field: 'user_key' }
      ],
      association: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'association_type', data: 'association_type' },
        { label: 'address_type', data: 'address_type' },
        { label: 'visibility', data: 'visibility' },
        { label: 'address', data: 'address' }
      ],
      leave: [
        { label: 'leave_type', data: 'leave_type' }
      ],
      manager: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'responsibility', data: 'responsibility' },
        { label: 'manager_type', data: 'manager_type' },
        { label: 'manager_level', data: 'manager_level' },
        { label: 'address_type', data: 'address_type' },
        { label: 'visibility', data: 'visibility' },
        { label: 'address', data: 'address' }
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

  methods: {
    loadContent (contentType, event) {
      let payload = {
        detail: contentType,
        validity: event,
        uuid: this.uuid
      }
      this.$emit('show', payload)
    }
  }
}
</script>
