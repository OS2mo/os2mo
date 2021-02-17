SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div id="app">
    <div class="container-fluid container-top-margin">
      <router-view/>
    </div>
  </div>
</template>


<script>

import { Conf } from '@/store/actions/conf'

export default {
  name: 'app',

  mounted () {
    var usersnapKey = process.env.USERSNAP_KEY || null
    if (usersnapKey) {
      var s = document.createElement('script')
      s.type = 'text/javascript'
      s.async = true
      s.src = `//api.usersnap.com/load/${usersnapKey}.js`
      var x = document.getElementsByTagName('script')[0]
      x.parentNode.insertBefore(s, x)
    }
  },

  created () {
    this.$store.dispatch(Conf.actions.SET_CONF_DB)
  }
}
</script>

<style>
  #app {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  .container-top-margin {
    margin-top: 4em;
  }
</style>
