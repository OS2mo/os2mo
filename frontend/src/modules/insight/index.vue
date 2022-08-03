SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card col">
    <div class="card-body d-flex flex-column">
      <h4 class="card-title" style="margin-bottom: 2rem">
        <icon name="exchange-alt" />
        {{ $tc("shared.insight", 2) }}
      </h4>
      <div v-if="query_files">
        <div v-for="(q, index) in query_files" :key="index">
          <input type="checkbox" :id="q" :value="q" v-model="chosen_files" />
          <label :for="q">{{ q }}</label>
        </div>
        <a href="#" @click="downloadZip">{{ $t("buttons.download_zip") }}</a>
      </div>
      <div v-if="!query_files || !query_files.length">
        <h5>{{ $t("common.no_files") }}</h5>
      </div>
      <div v-if="query_files">
        <b-tabs content-class="mt-3">
          <b-tab v-for="(q, index) in query_data" :key="index" :title="q.title">
            <data-grid
              :data-list="q.data"
              :data-fields="q.schema.fields"
              style="margin: 2rem 0"
            >
              <h5 style="margin: 1rem 0" slot="datagrid-header">{{ q.title }}</h5>
            </data-grid>
          </b-tab>
        </b-tabs>
      </div>
      <div v-if="!query_files || !query_files.length">
        <p>{{ $t("common.no_data") }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import Service from "@/api/HttpCommon"
import store from "./_store"
import { mapGetters } from "vuex"
import DataGrid from "../../components/DataGrid/DataGrid"
import bTabs from "bootstrap-vue/es/components/tabs/tabs"
import bTab from "bootstrap-vue/es/components/tabs/tab"

const STORE_KEY = "$_queryList"

export default {
  components: {
    DataGrid,
    bTabs,
    bTab,
  },
  data: function () {
    return {
      query_data: [],
      query_files: [],
      chosen_files: [],
    }
  },
  computed: {
    ...mapGetters(STORE_KEY, {
      queries: "getQueries",
    }),
  },
  watch: {
    chosen_files: function () {
      this.update()
    },
  },
  created() {
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
    getQueryString() {
      let file_query_string = ""

      if (this.chosen_files.length === 0) {
        file_query_string = "?q=all"
      } else {
        for (let i = 0; i < this.chosen_files.length; i++) {
          if (i === 0) {
            file_query_string += `?q=${this.chosen_files[0]}`
          } else {
            file_query_string += `&q=${this.chosen_files[i]}`
          }
        }
      }
      return file_query_string
    },
    update: function () {
      this.insightFiles()
      this.insightData(this.getQueryString())
    },
    handleError: function (error) {
      let thisComponent = this

      if (error.response.data.error_key === "E_DIR_NOT_FOUND") {
        alert(
          `${thisComponent.$t("alerts.error.E_DIRECTORY_NOT_SETUP_CORRECTLY")}
          ${thisComponent.$t("alerts.contact_admin")}

          ${error.response.data.description}
          ${error.response.data.directory}`
        )
      }
    },
    getInsightFiles: function () {
      return Service.get(`/insight/files`)
    },
    insightFiles: function () {
      this.getInsightFiles()
        .then((response) => {
          this.pushQueryFiles(response)
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    pushQueryFiles: function (response) {
      this.query_files = []
      let data = response.data
      for (let i = 0; i < data.length; i++) {
        this.query_files.push(data[i])
      }
    },
    getInsightData: function (query_string) {
      return Service.get(`/insight${query_string}`)
    },
    insightData: function (file_query_string) {
      this.getInsightData(file_query_string).then((response) => {
        this.pushQueryData(response)
      })
    },
    pushQueryData: function (response) {
      this.query_data = []
      let data = response.data
      for (let i = 0; i < data.length; i++) {
        this.query_data.push(data[i])
      }
    },
    downloadZip: function () {
      Service.download("/insight/download").then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement("a")
        link.href = url
        link.setAttribute("download", "insights.zip")
        document.body.appendChild(link)
        link.click()
      })
    },
  },
}
</script>

<style scoped>
.query-item {
  margin-bottom: 1rem;
}
</style>
