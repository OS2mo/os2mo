<template>
  <organisation-mapper
  @mapper:origin="onOrigin"
  @mapper:destination="onDestination"
  @mapper:submit="onSubmit"
  />
</template>

<script>
import OrganisationMapper from './_components/OrganisationMapper'
import store from './_store'
const STORE_KEY = '$_organisationMapper'

export default {
  name: 'OrganisationMapperModule',
  components: {
    OrganisationMapper
  },
  computed: {
  },
  created () {
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
  },
  beforeDestroy () {
    this.$store.unregisterModule(STORE_KEY)
  },
  methods: {
    onOrigin (val) {
      this.$store.commit(`${STORE_KEY}/SET_ORIGIN`, val)
    },

    onDestination (val) {
      this.$store.commit(`${STORE_KEY}/SET_DESTINATION`, val)
    },

    onSubmit () {
      this.$store.dispatch(`${STORE_KEY}/MAP_ORGANISATIONS`)
    }
  }
}
</script>
