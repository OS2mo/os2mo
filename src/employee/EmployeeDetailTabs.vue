<template>
  <div>
    <mo-loader v-show="isLoading"/>
    <b-tabs v-show="!isLoading" lazy>
      <b-tab :title="$t('tabs.employee.engagements')" active> 
        <mo-employee-detail 
          :uuid="uuid" 
          detail="engagement"
          :columns="engagement"
          :entry-component="components.engagement"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.addresses')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="address"
          :columns="address"
          :entry-component="components.address"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.roles')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="role"
          :columns="role"
          :entry-component="components.role"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.it')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="it"
          :columns="it"
          :entry-component="components.it"
        />
      </b-tab>
      <b-tab :title="$tc('tabs.employee.association', 2)">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="association"
          :columns="association"
          :entry-component="components.association"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.leave')">
        <mo-employee-detail 
          :uuid="uuid" 
          detail="leave"
          :columns="leave"
          :entry-component="components.leave"
        />
      </b-tab>
      <b-tab :title="$t('tabs.employee.manager')" >
        <mo-employee-detail 
          :uuid="uuid" 
          detail="manager"
          :columns="manager"
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
  import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'
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
        engagement: [
          {label: 'org_unit', data: 'org_unit'},
          {label: 'job_function', data: 'job_function'},
          {label: 'engagement_type', data: 'engagement_type'}
        ],
        role: [
          {label: 'org_unit', data: 'org_unit'},
          {label: 'role_type', data: 'role_type'}
        ],
        it: [
          {label: 'it_system', data: 'it_system'},
          {label: 'user_name', data: 'user_name'}
        ],
        association: [
          {label: 'org_unit', data: 'org_unit'},
          {label: 'job_function', data: 'job_function'},
          {label: 'association_type', data: 'association_type'},
          {label: 'address', data: 'address'},
          {label: 'address_type', data: 'address_type'}
        ],
        leave: [
          {label: 'leave_type', data: 'leave_type'}
        ],
        manager: [
          {label: 'org_unit', data: 'org_unit'},
          {label: 'responsibility', data: 'responsibility'},
          {label: 'manager_type', data: 'manager_type'},
          {label: 'manager_level', data: 'manager_level'},
          {label: 'address_type', data: 'address_type'},
          {label: 'address', data: 'address'}
        ],
        address: [
          {label: 'address_type', data: 'address_type'},
          {label: 'value', data: null}
        ],
        components: {
          engagement: MoEngagementEntry,
          address: MoAddressEntry,
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
