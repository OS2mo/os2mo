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
  </div>
</template>

<script>
/**
 * A landing page component.
 */
import Frontpage from '@/api/Frontpage'

export default {
  data () {
    return {
      menu: []
    }
  },

  created () {
    this.menu = Frontpage.getMenu()
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

  h1,h4 {
    color: #ffffff;
  }
</style>
