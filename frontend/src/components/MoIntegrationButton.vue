SPDX-FileCopyrightText: 2020-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <button class="btn btn-outline-primary" v-on:click="submit()">
      <icon name="sync" v-if="!isLoading" />
      <icon name="sync" spin v-if="isLoading" />
    </button>
  </div>
</template>

<script>
import Service from "@/api/HttpCommon"

export default {
  props: {
    uuid: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      isLoading: false,
    }
  },

  methods: {
    submit() {
      if (this.isLoading) {
        return
      }
      this.isLoading = true
      return Service.get(`/ou/${this.uuid}/refresh`)
        .then((response) => {
          this.$store.commit("log/newWorkLog", {
            type: "ORGANISATION_EXTERNAL_FUNCTION",
            value: { message: response.data.message },
          })
        })
        .catch((error) => {
          this.$store.commit("log/newError", { type: "ERROR", value: error.response })
        })
        .finally(() => {
          this.isLoading = false
        })
    },
  },
}
</script>
