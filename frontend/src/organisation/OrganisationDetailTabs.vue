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
  import MoOrganisationUnitDetail from './MoOrganisationUnitDetail'
  import MoOrganisationUnitEntry from '@/components/MoEntry/MoOrganisationUnitEntry'
  import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'

  export default {
    components: {
      MoOrganisationUnitDetail
    },

    props: {
      uuid: {type: String, required: true},
      atDate: [Date, String],
      timemachineFriendly: Boolean
    },

    data () {
      return {
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
        manager: [
          {label: 'person', data: 'person'},
          {label: 'responsibility', data: 'responsibility'},
          {label: 'manager_type', data: 'manager_type'},
          {label: 'manager_level', data: 'manager_level'},
          {label: 'address_type', data: 'address_type'},
          {label: 'address', data: 'address'}
        ],
        components: {
          orgUnit: MoOrganisationUnitEntry,
          address: MoAddressEntry
        }
      }
    }
  }
</script>
