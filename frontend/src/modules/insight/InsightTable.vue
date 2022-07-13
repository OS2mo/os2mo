<!--
SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
-->
<template>
    <data-grid :data-list="table_data" :data-fields="table_fields" style="margin-top: 0; margin-bottom: 2rem;">
        <header class="insights-table-header" slot="datagrid-header">
            <h5 style="margin-top: 0.5rem">{{ table_title }}</h5>
            <button class="btn" style="margin-left: 1rem;" @click="downloadCSVData">Download CSV (If download doesn't start, disable AdBlock)</button>
        </header>
    </data-grid>
</template>

<script>
import DataGrid from '../../components/DataGrid/DataGrid.vue'
import { get_by_graphql } from '@/api/HttpCommon'

export default {
    components: {
        DataGrid
    },
    data: function() {
        return {
            table_data: [],
            table_fields: [],
            table_title: 'Medarbejdere (via GraphQL)',

            // TODO: REDO query when improved filtering has been implemented
            // This query hardcodes some specific users to avoid performance issues
            // and it suffers from a general lack of filterability (ie lists all addresses).
            // This is NOT meant for production use.
            query: `{
                managers(uuids: "0b51953c-537b-4bf9-a872-2710b0ddd9e3") {
                  objects {
                    user_key
                    org_unit {
                      engagements {
                        employee {
                          user_key
                          name
                          itusers {
                            user_key
                            itsystem_uuid
                          }
                          addresses {
                            address_type {
                              scope
                            }
                            value
                          }
                        }
                      }
                    }
                  }
                }
                itsystems {
                  name
                  uuid
                }
              }`
        }
    },
    watch: {
      '$i18n.locale': function() {
      this.updateView(this.query);
      }
    },
    methods: {
        configColumns: function(data) {
          const fields = [
            {name: this.$t('table_headers.employee_name'), class: ''},
            {name: this.$t('table_headers.employee_email'), class: ''},
            {name: this.$t('table_headers.it_system'), class: ''},
            {name: this.$t('table_headers.user_key'), class: ''},
          ]

          return fields
        },
        fetchData: function(query) {
            return get_by_graphql(query)
        },
        sanitizeData: function(data) {
          const row_data = [];
          const fields = this.configColumns(data)
          const employees = data.managers[0].objects[0].org_unit[0].engagements;
          const it_systems = data.itsystems
          
          for (let i = 0; i < employees.length; i++) {
            let row = { id: `id${i}` };
            let employee = employees[i].employee[0]
            row[fields[0].name] = employee.name;
            row[fields[1].name] = this.generateEmailString(employee.addresses);
            if(employee.itusers.length > 0) {
              // F... this line - field returns undefined in front of uuids if it's not there
              row[fields[2].name] = ``
              row[fields[3].name] = ``
              for (let j = 0; j < employee.itusers.length; j++) {
                row[fields[2].name] += `${this.getItSystem(employee.itusers[j].itsystem_uuid, it_systems)}`
                row[fields[3].name] += `${employee.itusers[j].user_key}`
                // Add comma, if not last iteration
                if (j !== employee.itusers.length-1){
                  row[fields[2].name] += `, `
                  row[fields[3].name] += `, `
                }
              }
            }
            row_data.push(row);
          }
          return row_data;
        },
        generateEmailString: function(addresses) {
          // Changed this to faster loop
          for (let i=0; i<addresses.length; i++){
            if(addresses[i].address_type.scope === 'EMAIL') {
              return addresses[i].value
            }
          }
        },
        downloadCSVData: function() {
            let rows = Array.from(this.table_data)
            let csvContent =
              `data:text/csv;charset=utf-8,${this.$t('table_headers.employee_name')},${this.$t('table_headers.employee_email')},${this.$t('table_headers.it_system')},${this.$t('table_headers.user_key')}` +
              rows.map(row => {
                return `\n${ row[this.$t('table_headers.employee_name')] },${ row[this.$t('table_headers.employee_email')] },${ row[this.$t('table_headers.it_system')] },${ row[this.$t('table_headers.user_key')] }`
              })
            const encodedUri = encodeURI(csvContent)
            window.open(encodedUri)
        },
        getItSystem: function(uuid, it_systems) {
          // infinite faster than option 2 (according to my test at least)
          for (let i=0; i<it_systems.length; i++){
            if(it_systems[i].uuid === uuid) {
              return it_systems[i].name
            }
          }

          // Different approach - option 2
          
          // let it_system_str = ''
          // const it_systems = it_systems_array.filter(it_system => {
          //   return it_system.uuid === uuid
          // })
          // it_systems.forEach(it_system => {
          //   it_system_str += `${it_system.name}`
          // })
          // return it_system_str


          // hate this - but i needed to change some major logic to avoid it.
          
          // if(uuid == "49d91308-67b0-4b8c-b787-1cd58e3039bd") {
          //   return "SAP"
          // }
          // if(uuid == "5168dd45-4cb5-4932-b8a1-10dbe736fc5d") {
          //   return "Office365"
          // }
          // if(uuid == "988dead8-7564-464a-8339-b7057bfa2665") {
          //   return "Plone"
          // }
          // if(uuid == "a1608e69-c422-404f-a6cc-b873c50af111") {
          //   return "Active Directory"
          // }
          // if(uuid == "db519bfd-0fdd-4e5d-9337-518d1dbdbfc9") {
          //   return "OpenDesk"
          // }
        },
        updateView: function(query) {
          this.fetchData(query)
          .then((response) => {
              this.table_fields = this.configColumns(response.data.data)
              this.table_data = this.sanitizeData(response.data.data)
              // prefer this, but with current solution I need 'itsystems'
              // this.table_data = this.sanitizeData(response.data.data.managers[0].objects[0].org_unit[0].engagements)

          })
        }
    },
    created: function() {
        this.updateView(this.query)
    }
}
</script>

<style scoped>
.insights-table-header {
  display: flex; 
  align-items: center;
  margin-top: 0rem; 
  margin-bottom: 1rem; 
  margin-right: 0; 
  margin-left: 0; 
}
</style>
