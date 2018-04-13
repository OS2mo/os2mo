<template>
  <div>
    <loading v-show="isLoading"/>
    <b-tabs v-show="!isLoading" lazy>
      <b-tab title="Engagement" active> 
        <mo-employee-detail 
          :uuid="uuid" 
          detail="engagement"
          :columns="columns.engagement"
          :entry-component="components.engagement"
        />
      </b-tab>
      <b-tab title="Adresser">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="address"
          :columns="columns.address"
          :entry-component="components.address"
        />
      </b-tab>
      <b-tab title="Rolle">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="role"
          :columns="columns.role"
          :entry-component="components.role"
        />
      </b-tab>
      <b-tab title="IT">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="it"
          :columns="columns.it"
          :entry-component="components.it"
        />
      </b-tab>
      <b-tab title="Tilknytning">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="association"
          :columns="columns.association"
          :entry-component="components.association"
        />
      </b-tab>
      <b-tab title="Orlov">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="leave"
          :columns="columns.leave"
          :entry-component="components.leave"
        />
      </b-tab>
      <b-tab title="Leder" >
        <mo-employee-detail 
          :uuid="uuid" 
          detail="manager"
          :columns="columns.manager"
          :entry-component="components.manager"
        />
      </b-tab>
    </b-tabs>
  </div>
</template>


<script>
  import Loading from '../components/Loading'
  import MoEmployeeDetail from './MoEmployeeDetail'
  import MoEngagementEntry from './MoEngagement/MoEngagementEntry'
  import MoRoleEntry from './MoRole/MoRoleEntry'
  import MoItSystemEntry from './MoItSystem/MoItSystemEntry'
  import MoAssociationEntry from './MoAssociation/MoAssociationEntry'
  import MoLeaveEntry from './MoLeave/MoLeaveEntry'
  import MoManagerEntry from './MoManager/MoManagerEntry'
  import MoAddressEntry from '@/components/MoAddressEntry/MoAddressEntry'

  export default {
    components: {
      Loading,
      MoEmployeeDetail
    },
    props: {
      uuid: String
    },
    data () {
      return {
        isLoading: false,
        columns: {
          engagement: ['org_unit', 'job_function', 'engagement_type'],
          role: ['org_unit', 'role_type'],
          it: ['it_system', 'user_name'],
          association: ['org_unit', 'job_function', 'association_type', 'address', 'address_type'],
          leave: ['leave_type'],
          manager: ['org_unit', 'responsibility', 'manager_type', 'manager_level', 'address_type', 'address'],
          address: ['address_type', null]
        },
        components: {
          engagement: MoEngagementEntry,
          role: MoRoleEntry,
          it: MoItSystemEntry,
          association: MoAssociationEntry,
          leave: MoLeaveEntry,
          manager: MoManagerEntry,
          address: MoAddressEntry
        }
      }
    }
  }
</script>
