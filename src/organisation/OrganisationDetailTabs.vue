<template>
  <div>
    <b-tabs lazy>
      <b-tab title="Enhed" active>
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="org_unit"
          :columns="columns.org_unit"
          :entry-component="timemachineFriendly ? undefined : components.orgUnit"
          hide-create
        />
      </b-tab>
      <b-tab title="Adresse">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="address"
          :columns="columns.address"
          :entry-component="timemachineFriendly ? undefined : components.address"
        />
      </b-tab>
      <b-tab title="Engagementer">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="engagement"
          :columns="columns.engagement"
        />
      </b-tab>
      <b-tab title="Tilknytninger">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="association"
          :columns="columns.association"
        />
      </b-tab>
      <b-tab title="Rolle">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="role"
          :columns="columns.role"
        />
      </b-tab>
      <b-tab title="Leder">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          :at-date="atDate"
          detail="manager"
          :columns="columns.manager"
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
  import MoOrganisationUnitDetail from './MoOrganisationUnitDetail'
  import MoOrganisationUnitEntry from './MoOrganisationUnit/MoOrganisationUnitEntry'
  import MoAddressEntry from '../components/MoAddressEntry/MoAddressEntry'
  import MoAddMany from '../components/MoAddMany'

  export default {
    components: {
      MoOrganisationUnitDetail,
      MoAddMany
    },
    props: {
      uuid: {
        type: String,
        required: true
      },
      atDate: [Date, String],
      timemachineFriendly: Boolean
    },
    data () {
      return {
        columns: {
          org_unit: [null, 'org_unit_type', 'parent'],
          address: ['address_type', null],
          engagement: ['person', 'engagement_type', 'job_function', 'org_unit'],
          association: ['person', 'association_type', 'job_function', 'address', 'address_type', 'org_unit'],
          role: ['person', 'role_type'],
          manager: ['person', 'responsibility', 'manager_type', 'manager_level', 'address_type', 'address']
        },
        components: {
          orgUnit: MoOrganisationUnitEntry,
          address: MoAddressEntry
        }
      }
    }
  }
</script>
