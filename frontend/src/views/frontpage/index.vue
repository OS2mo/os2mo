SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
      <div class="col text-center">
        <h1>{{$t('common.welcome_message')}}</h1>
        <h4>{{$t('common.welcome_tagline')}}</h4>
      </div>
    </nav>

    <div id="login-wrapper">
      <div v-for="(m, index) in menu" :key="index" class="col">
        <component :is="m.template"/>
      </div>
    </div>
    <div class="version">
      <div>
        <a href="https://os2mo.readthedocs.io/en/development/news.html">
          {{this.mo_version}}</a>
      </div>
      <div>
        <a href="https://mox.readthedocs.io/en/development/dev/news/">
          {{this.lora_version}}</a>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * A landing page component.
 */
import Frontpage from '@/api/Frontpage'
import Version from '@/api/Version'

export default {
  data () {
    return {
      menu: [],
      mo_version: null,
      lora_version: null
    }
  },

  created () {
    this.menu = Frontpage.getMenu()

    Version.get().then(response => {
      const version_dict = response.data
      this.mo_version = `OS2mo ${version_dict['mo_version']}`
      this.lora_version = `LoRa ${version_dict['lora_version']}`
    })
  },

  methods: {
    /**
     * Push route to destination.
     */
    setDestination (val) {
      this.$router.push({
        name: val
      })
    }
  }
}
</script>

<style scoped>
  #login-wrapper {
    text-align: center;
    margin-top: 10em;
  }

  .version {
    position: absolute;
    bottom: 1em;
    left: 1em;
  }

  h1, h4 {
    color: #ffffff;
  }
</style>
