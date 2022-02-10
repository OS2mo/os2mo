<template>
    <data-grid :data-list="table_data" :data-fields="table_fields" style="margin: 2rem 0;">
        <h5 style="margin: 1rem 0;" slot="datagrid-header">{{ table_title }}</h5>
    </data-grid>
</template>

<script>
import DataGrid from '../../components/DataGrid/DataGrid.vue'
import Service from '@/api/HttpCommon'

export default {
    components: {
        DataGrid
    },
    data: function() {
        return {
            table_data: [],
            table_fields: [],
            table_title: 'GraphQL Data test',
            query: `query: "{
                employees {
                    name
                }
            }"`
        }
    },
    methods: {
        configColumns: function(data) {
            return fields
        },
        fetchData: function(query) {
            return Service.post('http://localhost:5000/graphql', query)
        },
        sanitizeData: function(data) {
            const row_data = []
            return row_data
        },
        updateView: function(query) {

            this.fetchData(query)
            .then((response) => {
                this.table_fields = this.configColumns(response.data.data)
                this.table_data = this.sanitizeData(response.data.data)
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
