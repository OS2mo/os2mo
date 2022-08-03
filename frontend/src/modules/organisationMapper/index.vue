SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <h3>{{ $t("shared.organisation_mapping") }}</h3>

    <div class="row">
      <div class="col">
        <div class="card">
          <mo-org-tree-view class="card-body origin" v-model="origin" />
        </div>

        <button
          @click="onSubmit"
          class="mt-2 btn btn-primary btn-submit"
          :disabled="!isDirty"
        >
          <icon name="sitemap" />
          {{ $t("buttons.save") }}
        </button>
      </div>

      <div class="col">
        <div class="card">
          <mo-org-tree-view
            multiple
            v-model="destination"
            :disabled-unit="origin"
            class="card-body destination"
            v-if="origin"
          />
          <div class="card-body" v-else>
            <p class="card-text">
              {{ $t("organisationMapper.help") }}
            </p>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <mo-log class="card" />
      </div>
    </div>
  </div>
</template>

<script>
import MoOrgTreeView from "@/components/MoTreeView/MoOrgTreeView"
import MoLog from "@/components/MoLog/MoLog"
import { mapGetters } from "vuex"
import store from "./_store"
import mainStore from "@/store"

mainStore.registerModule("organisationMapper", store)

export default {
  name: "OrganisationMapperModule",
  components: {
    MoLog,
    MoOrgTreeView,
  },
  computed: {
    origin: {
      get() {
        return this.$store.getters["organisationMapper/origin"]
      },
      set(val) {
        this.$store.commit("organisationMapper/SET_ORIGIN", val)
      },
    },

    destination: {
      get() {
        return this.$store.getters["organisationMapper/destination"]
      },
      set(val) {
        this.$store.commit("organisationMapper/SET_DESTINATION", val)
        return this.$store.getters["organisationMapper/destination"]
      },
    },

    ...mapGetters({
      isDirty: "organisationMapper/isDirty",
    }),
  },

  watch: {
    origin(newVal) {
      this.$store.dispatch("organisationMapper/GET_ORGANISATION_MAPPINGS")
    },
  },

  methods: {
    onSubmit() {
      this.$store.dispatch("organisationMapper/MAP_ORGANISATIONS")
    },
  },
}
</script>

<style scoped>
.mapper-column {
  min-height: 10em;
  margin-bottom: 1em;
}
</style>
