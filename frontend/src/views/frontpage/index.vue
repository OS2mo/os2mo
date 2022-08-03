SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
      <mo-locale-picker />
      <div class="col text-center">
        <h1>{{ $t("common.welcome_message") }}</h1>
        <h4>{{ $t("common.welcome_tagline") }}</h4>
      </div>
    </nav>
    <div id="main-menu">
      <div v-for="(m, index) in menu" :key="index" class="col">
        <component :is="m.template" />
      </div>
    </div>
    <div class="version">
      <div>
        <a href="https://rammearkitektur.docs.magenta.dk/os2mo/news.html">
          {{ this.mo_version }}
        </a>
      </div>
      <div>
        <a href="https://mox.readthedocs.io/en/master/dev/news.html">
          {{ this.lora_version }}
        </a>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * A landing page component.
 */
import Frontpage from "@/api/Frontpage"
import Version from "@/api/Version"
import MoLocalePicker from "@/components/MoLocalePicker.vue"

export default {
  components: {
    MoLocalePicker,
  },

  data() {
    return {
      menu: [],
      mo_version: null,
      lora_version: null,
    }
  },

  created() {
    this.menu = Frontpage.getMenu()

    Version.get().then((response) => {
      const version_dict = response.data
      const mo_hash = (version_dict["mo_hash"] || "").substring(0, 8)
      this.mo_version = `OS2mo ${version_dict["mo_version"]}@${mo_hash}`
      this.lora_version = `LoRa ${version_dict["lora_version"]}`
    })
  },

  methods: {
    /**
     * Push route to destination.
     */
    setDestination(val) {
      this.$router.push({
        name: val,
      })
    },
  },
}
</script>

<style scoped>
#main-menu {
  text-align: center;
  margin-top: 10em;
}

#locale-picker {
  position: absolute;
  top: 0.5em;
  right: 0.5em;
  z-index: 1111;
}

.version {
  position: absolute;
  bottom: 1em;
  left: 1em;
}

nav {
  height: auto;
}

h1,
h4 {
  color: #ffffff;
}
</style>
