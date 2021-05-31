SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card col">
    <div class="card-body d-flex flex-column">
      <h4 class="card-title" style="margin-bottom: 2rem;">
        <icon name="exchange-alt"/>
        {{$tc('shared.query', 2)}}
      </h4>

      <b-tabs content-class="mt-3">
        <b-tab 
          v-for="(q, index) in query_data"
          :key="index"
          :title="q.title">
          <data-grid :data-list="q.data" :data-fields="q.schema.fields" style="margin: 2rem 0;">
            <h5 style="margin: 1rem 0;" slot="datagrid-header">{{q.title}}</h5>
          </data-grid>
        </b-tab>
      </b-tabs>

    </div>
  </div>
</template>

<script>
import Service from '@/api/HttpCommon'
import store from './_store'
import { mapGetters } from 'vuex'
import DataGrid from '../../components/Datagrid/DataGrid'
import bTabs from 'bootstrap-vue/es/components/tabs/tabs'
import bTab from 'bootstrap-vue/es/components/tabs/tab'

const STORE_KEY = '$_queryList'

export default {
  components: {
    DataGrid,
    bTabs,
    bTab
  },
  data: function() {
    return {
      query_data: []
    }
  },
  computed: {
    ...mapGetters(STORE_KEY, {
      queries: 'getQueries'
    })
  },
  created () {
    // This might be unnecessary in the future
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
    this.$store.dispatch(`${STORE_KEY}/getQueries`)

    // Get all the query data from dummy JSON files
    this.update()

  },
  methods: {
    downloadLink(file) {
      return "/service/exports/" + file
    },

    update: function() {
      Service.get('../dummy-data/all_leader_functions.json')
      .then(response => {
        let data = response.data
        data.title='Alle Lederfunktioner'
        this.query_data.push(data)
      })
      Service.get('../dummy-data/all_engagements.json')
      .then(response => {
        let data = response.data
        data.title = 'Alle Stillinger'
        this.query_data.push(data)
      })
      Service.get('../dummy-data/orgs_and_engagements.json')
      .then(response => {
        let data = response.data
        data.title = 'Organisationsstruktur og Stillinger'
        this.query_data.push(data)
      })
      Service.get('../dummy-data/orgunits.json')
      .then(response => {
        let data = response.data
        data.title = 'Organisationsenheder'
        this.query_data.push(data)
      })
      Service.get('../dummy-data/sd_and_p_no.json')
      .then(response => {
        let data = response.data
        data.title = 'SDLønorganisation og P-Nummer'
        this.query_data.push(data)
      })
    }
  }
}
</script>

<style scoped>
  .query-item {
    margin-bottom: 1rem;
  }
</style>
