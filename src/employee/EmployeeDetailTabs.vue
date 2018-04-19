<template>
  <div>
    <mo-loader v-show="isLoading"/>
    <b-tabs v-show="!isLoading" lazy>
      <b-tab :title="$t('tabs.employee.engagements')" active> 
        <mo-employee-detail 
          :uuid="uuid" 
          detail="engagement"
          :columns="columns.engagement"
          :entry-component="components.engagement"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.addresses')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="address"
          :columns="columns.address"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.roles')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="role"
          :columns="columns.role"
          :entry-component="components.role"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.it')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="it"
          :columns="columns.it"
          :entry-component="components.it"
        />
      </b-tab>
      <b-tab :title="$tc('tabs.employee.association', 2)">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="association"
          :columns="columns.association"
          :entry-component="components.association"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.leave')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="leave"
          :columns="columns.leave"
          :entry-component="components.leave"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.manager')" >
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
  import MoLoader from '@/components/atoms/MoLoader'
  import MoEmployeeDetail from './MoEmployeeDetail'
  import MoEngagementEntry from '@/components/MoEntry/MoEngagementEntry'
  import MoRoleEntry from '@/components/MoEntry/MoRoleEntry'
  import MoItSystemEntry from '@/components/MoEntry/MoItSystemEntry'
  import MoAssociationEntry from '@/components/MoEntry/MoAssociationEntry'
  import MoLeaveEntry from '@/components/MoEntry/MoLeaveEntry'
  import MoManagerEntry from '@/components/MoEntry/MoManagerEntry'

  export default {
    components: {
      MoLoader,
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
          manager: MoManagerEntry
        }
      }
    }
  }
</script>
