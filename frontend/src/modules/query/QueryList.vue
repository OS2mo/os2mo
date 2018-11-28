<template>
  <div class="card col">
    <div class="card-body d-flex flex-column">
      <h4 class="card-title">
        <icon name="exchange-alt"/>
        {{$tc('shared.query', 2)}}
      </h4>
      <span v-for="(q, index) in queries" :key="index">
        <icon name="download"/>
      <a href="#" @click="$store.dispatch('$_queryList/downloadFile', q)">{{q}}</a>
      </span>
    </div>
  </div>
</template>

<script>
import store from './_store'
import { mapGetters } from 'vuex'

export default {
  computed: {
    ...mapGetters({
      queries: '$_queryList/getQueries'
    })
  },
  created () {
    const STORE_KEY = '$_queryList'
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
  },
  mounted () {
    this.$store.dispatch('$_queryList/getQueries')
  }
}
</script>
