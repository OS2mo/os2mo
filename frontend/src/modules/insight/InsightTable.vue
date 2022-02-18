<template>
    <data-grid :data-list="table_data" :data-fields="table_fields" style="margin: 2rem 0;">
        <header style="margin: 1rem 0; display: flex; align-items: center;" slot="datagrid-header">
            <h5>{{ table_title }}</h5>
            <button class="btn" style="margin-left: 1rem;" @click="downloadCSVData">Download CSV</button>
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
                employees(uuids: [
                    "0004b952-a513-430b-b696-8d393d7eb2bb",
                    "002a1aed-d015-4b86-86a4-c37cd8df1e18",
                    "00556594-7be8-4c57-ba0a-9d2adefc8d1c",
                    "00973369-2d8f-4120-bbaf-75f0e0f38534",
                    "00b49064-259d-49b4-bc64-71ab9b07d88f",
                    "01f80cbc-da79-45e8-8cb2-ee9582eae785"
                    ]) {
                    name,
                    engagements {
                        org_unit {
                            name,
                            managers(inherit: true) {
                                employee {
                                    name,
                                    addresses {
                                        address_type {
                                            name,
                                            scope
                                        }
                                        value
                                    }
                                }
                            }
                        }
                    }
                    addresses {
                        address_type {
                            name,
                            scope
                        }
                        value
                    }
                }
            }`
        }
    },
    methods: {
        configColumns: function(data) {
            const fields = [
                {name: 'Medarbejder navn', class: ''}, 
                {name: 'Medarbejder email', class: ''}, 
                {name: 'Lederens navn', class: ''},
                {name: 'Lederens email', class: ''},
                {name: 'Afdelingsnavn', class: ''}
            ]
            return fields
        },
        fetchData: function(query) {
            return get_by_graphql(query)
        },
        sanitizeData: function(data) {
            // TODO: Don't hardcode field names
            const row_data = []
            for (let i = 0; i < data.length; i++) {
                let row = {id: `id${ i }`}
                
                row['Medarbejder navn'] = data[i].name
                
                row['Medarbejder email'] = this.generateEmailString(data[i].addresses)

                if (data[i].engagements[0]) {
                    const manager = data[i].engagements[0].org_unit.managers[0].employee
                    row['Lederens navn'] = manager.name
                    row['Lederens email'] = this.generateEmailString(manager.addresses)
                    row['Afdelingsnavn'] = data[i].engagements[0].org_unit.name
                }
                
                row_data.push(row)
            }
            return row_data
        },
        generateEmailString: function(addresses) {
            let email_str = ''
            const emails = addresses.filter(addr => {
                    return addr.address_type.scope === 'EMAIL'
                })
            emails.forEach(email => {
                email_str += `${ email.value } `
            })
            return email_str
        },
        downloadCSVData: function() {
            // TODO: Don't hardcode field names
            let rows = Array.from(this.table_data)
            let csvContent = "data:text/csv;charset=utf-8,Medarbejder navn,Medarbejder email,Lederens navn,Lederens email,Afdelingsnavn" + rows.map(row => {
                return `\n${ row['Medarbejder navn'] },${ row['Medarbejder email'] },${ row['Lederens navn'] },${ row['Lederens email'] },${ row['Afdelingsnavn'] }`
            })
            const encodedUri = encodeURI(csvContent)
            window.open(encodedUri)
        },
        updateView: function(query) {

            this.fetchData(query)
            .then((response) => {
                this.table_fields = this.configColumns(response.data.data)
                this.table_data = this.sanitizeData(response.data.data.employees)
            })
        }
    },
    created: function() {
  
        this.updateView(this.query)
    }
}
</script>

<style scoped>

</style>
