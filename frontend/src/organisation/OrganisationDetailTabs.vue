<template>
  <div>
    <b-tabs lazy>
      <b-tab :title="$t('tabs.organisation.unit')" active>
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="org_unit"
          :columns="org_unit"
          :entry-component="timemachineFriendly ? undefined : components.orgUnit"
          hide-create
        />
      </b-tab>

      <b-tab :title="$t('tabs.organisation.addresses')">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="address"
          :columns="address"
          :entry-component="timemachineFriendly ? undefined : components.address"
        />
      </b-tab>

      <b-tab :title="$t('tabs.organisation.engagements')">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="engagement"
          :columns="engagement"
        />
      </b-tab>

      <b-tab :title="$tc('tabs.organisation.association', 2)">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="association"
          :columns="association"
        />
      </b-tab>

      <b-tab :title="$t('tabs.organisation.it')">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="it"
          :columns="it"
        />
      </b-tab>

      <b-tab :title="$t('tabs.organisation.roles')">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="role"
          :columns="role"
        />
      </b-tab>

      <b-tab :title="$t('tabs.organisation.managers')">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="manager"
          :columns="manager"
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
  /**
   * A organisation detail tabs component.
   */

  import MoOrganisationUnitDetail from './MoOrganisationUnitDetail'
  import MoOrganisationUnitEntry from '@/components/MoEntry/MoOrganisationUnitEntry'
  import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'

  export default {
    components: {
      MoOrganisationUnitDetail
    },

    props: {
      /**
       * Defines a unique identifier which must be unique.
       */
      uuid: {type: String, required: true},

      /**
       * Defines a at date.
       */
      atDate: [Date, String],

      /**
       * This Boolean property indicates the timemachine output.
       */
      timemachineFriendly: Boolean
    },

    data () {
      return {
        /**
        * The org_unit, address, engagement, association, role, manager component value.
        * Used to detect changes and restore the value for columns.
        */
        org_unit: [
          {label: 'org_unit', data: null},
          {label: 'org_unit_type', data: 'org_unit_type'},
          {label: 'parent', data: 'parent'}
        ],
        address: [
          {label: 'address_type', data: 'address_type'},
          {label: 'address', data: null}
        ],
        engagement: [
          {label: 'person', data: 'person'},
          {label: 'engagement_type', data: 'engagement_type'},
          {label: 'job_function', data: 'job_function'},
          {label: 'org_unit', data: 'org_unit'}
        ],
        association: [
          {label: 'person', data: 'person'},
          {label: 'association_type', data: 'association_type'},
          {label: 'job_function', data: 'job_function'},
          {label: 'address_type', data: 'address_type'},
          {label: 'address', data: 'address'},
          {label: 'org_unit', data: 'org_unit'}
        ],
        role: [
          {label: 'person', data: 'person'},
          {label: 'role_type', data: 'role_type'}
        ],
        it: [
          {label: 'it_system', data: 'itsystem'},
          {label: 'user_name', data: null, field: 'user_key'}
        ],
        manager: [
          {label: 'person', data: 'person'},
          {label: 'responsibility', data: 'responsibility'},
          {label: 'manager_type', data: 'manager_type'},
          {label: 'manager_level', data: 'manager_level'},
          {label: 'address_type', data: 'address_type'},
          {label: 'address', data: 'address'}
        ],

        /**
         * The MoOrganisationUnitEntry, MoAddressEntry component.
         * Used to add edit and create for orgUnit and address.
         */
        components: {
          orgUnit: MoOrganisationUnitEntry,
          address: MoAddressEntry
        }
      }
    }
  }
</script>
