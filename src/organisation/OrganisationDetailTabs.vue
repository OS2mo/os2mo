<template>
  <div>
    <b-tabs lazy>
      <b-tab title="Enhed" active>
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          detail="org_unit"
          :columns="columns.org_unit"
          :entry-component="components.orgUnit"
        />
      </b-tab>
      <b-tab title="Adresse">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          detail="address"
          :columns="columns.address"
        />
      </b-tab>
      <b-tab title="Engagementer">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          detail="engagement"
          :columns="columns.engagement"
        />
      </b-tab>
      <b-tab title="Tilknytninger">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          detail="association"
          :columns="columns.association"
        />
      </b-tab>
      <b-tab title="Rolle">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          detail="role"
          :columns="columns.role"
        />
      </b-tab>
      <b-tab title="Leder">
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          detail="manager"
          :columns="columns.manager"
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import MoOrganisationUnitDetail from './MoOrganisationUnitDetail'
  import OrganisationDetailUnit from './OrganisationDetailUnit'
  import MoOrganisationUnitEntry from './MoOrganisationUnit/MoOrganisationUnitEntry'

  export default {
    components: {
      MoOrganisationUnitDetail,
      OrganisationDetailUnit
    },
    props: {
      uuid: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        tabs: {},
        columns: {
          org_unit: [null, 'org_unit_type', 'parent'],
          address: ['address_type', null],
          engagement: ['person', 'engagement_type', 'job_function', 'org_unit'],
          association: ['person', 'association_type', 'job_function', 'address', 'address_type', 'org_unit'],
          role: ['person', 'role_type'],
          manager: ['person', 'responsibility', 'manager_type', 'manager_level', 'address_type', 'address']
        },
        components: {
          orgUnit: MoOrganisationUnitEntry
        }
      }
    },
    created () {
      this.getTabs()
    },
    methods: {
      getTabs () {
        OrganisationUnit.getDetailList(this.uuid)
          .then(respone => {
            this.tabs = respone
          })
      }
    }
  }
</script>
