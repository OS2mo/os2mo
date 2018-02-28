<template>
  <div>
    <b-tabs>
      <b-tab title="Enhed" active>
        <mo-organisation-unit-detail 
          :uuid="uuid" 
          detail="info"
          :columns="columns.org_unit"
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
      <!--
      <b-tab title="Enhed" active> 
        <organisation-detail-unit :uuid="uuid"/>
      </b-tab>
      <b-tab title="Lokation">
        <organisation-detail-location :uuid="uuid"/>
      </b-tab>
      <b-tab title="Kontaktkanal">
        <organisation-detail-contact :uuid="uuid"/>
      </b-tab>
      <b-tab title="Engagementer" v-if="tabs.engagement">
        <organisation-detail-engagement :uuid="uuid"/>
      </b-tab>
      <b-tab title="Tilknytninger" v-if="tabs.association">
      </b-tab>
      -->
    </b-tabs>
  </div>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import MoOrganisationUnitDetail from './MoOrganisationUnitDetail'
  import OrganisationDetailUnit from './OrganisationDetailUnit'
  import OrganisationDetailLocation from './OrganisationDetailLocation'
  import OrganisationDetailContact from './OrganisationDetailContact'
  import OrganisationDetailEngagement from './OrganisationDetailEngagement'

  export default {
    components: {
      MoOrganisationUnitDetail,
      OrganisationDetailUnit,
      OrganisationDetailLocation,
      OrganisationDetailContact,
      OrganisationDetailEngagement
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
          org_unit: ['org_unit', 'org_unit_type', 'parent'],
          engagement: ['person', 'engagement_type', 'job_function', 'org_unit'],
          association: ['person', 'association_type', 'job_function', 'org_unit'],
          role: ['person', 'role_type'],
          manager: ['person', 'responsibility', 'manager_type', 'manager_level']
        },
        components: {
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
