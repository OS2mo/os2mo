<template>
  <organisation-mapper/>
</template>

<script>
import OrganisationMapper from './_components/OrganisationMapper'
// import store from './_store'

export default {
  name: 'OrganisationMapperModule',
  components: {
    OrganisationMapper
  },
  computed: {
  },
  created () {
    const STORE_KEY = '$_chat'

    if (!(STORE_KEY in this.$store._modules.root._children)) {
      // this.$store.registerModule(STORE_KEY, store)
    }
  },
  mounted () {
    // this.$store.dispatch('$_chat/getMessages')
  }
}
</script>