<template>
  <div v-if="orgUnitInfo.user_settings.orgunit">
    <b-tabs lazy>
      <b-tab :title="$t('tabs.organisation.unit')" active>
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

      <b-tab :title="$t('tabs.organisation.addresses')">
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

      <b-tab :title="$t('tabs.organisation.engagements')">
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['engagement']"
          content-type="engagement"
          :columns="engagement"
          @show="loadContent('engagement', $event)"
        />
      </b-tab>

      <b-tab :title="$tc('tabs.organisation.association', 2)">
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['association']"
          content-type="association"
          :columns="association"
          @show="loadContent('association', $event)"
        />
      </b-tab>

      <b-tab :title="$t('tabs.organisation.it')">
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

      <b-tab :title="$t('tabs.organisation.roles')" v-if="orgUnitInfo.user_settings.orgunit.show_roles">
        <mo-table-detail
          type="ORG_UNIT"
          :uuid="uuid"
          :content="content['role']"
          content-type="role"
          :columns="role"
          @show="loadContent('role', $event)"
        />
      </b-tab>

      <b-tab :title="$t('tabs.organisation.managers')">
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
    </b-tabs>
  </div>
</template>

<script>
/**
 * A organisation detail tabs component.
 */
import MoTableDetail from '@/components/MoTable/MoTableDetail'
import MoOrganisationUnitEntry from '@/components/MoEntry/MoOrganisationUnitEntry'
import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'
import MoItSystemEntry from '@/components/MoEntry/MoItSystemEntry'
import MoManagerEntry from '@/components/MoEntry/MoManagerEntry'
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
      // keep track of the latest tap shown
      latestTab: [],
      /**
       * The org_unit, address, engagement, association, role, manager component value.
       * Used to detect changes and restore the value for columns.
       */
      org_unit: [
        { label: 'org_unit', data: null },
        { label: 'org_unit_type', data: 'org_unit_type' },
        { label: 'parent', data: 'parent' }
      ],
      address: [
        { label: 'address_type', data: 'address_type' },
        { label: 'address', data: null }
      ],
      engagement: [
        { label: 'person', data: 'person' },
        { label: 'engagement_type', data: 'engagement_type' },
        { label: 'job_function', data: 'job_function' },
        { label: 'org_unit', data: 'org_unit' }
      ],
      association: [
        { label: 'person', data: 'person' },
        { label: 'association_type', data: 'association_type' },
        { label: 'job_function', data: 'job_function' },
        { label: 'address_type', data: 'address_type' },
        { label: 'address', data: 'address' },
        { label: 'org_unit', data: 'org_unit' }
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
        { label: 'manager_level', data: 'manager_level' },
        { label: 'address_type', data: 'address_type' },
        { label: 'address', data: 'address' }
      ],

      /**
       * The MoOrganisationUnitEntry, MoAddressEntry component.
       * Used to add edit and create for orgUnit and address.
       */
      components: {
        orgUnit: MoOrganisationUnitEntry,
        address: MoAddressEntry,
        itSystem: MoItSystemEntry,
        manager: MoManagerEntry
      }
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

  methods: {
    loadContent (contentType, event) {
      let payload = {
        detail: contentType,
        validity: event,
        uuid: this.uuid
      }
      this.latestTab = payload
      this.$emit('show', payload)
    }
  }
}
</script>
