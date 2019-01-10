<template>
  <div>
    <h1>{{$t('shared.organisation_mapping')}}</h1>

    <div class="row">
      <div class="col">
        <div class="card">
          <mo-tree-view class="card-body" v-model="origin"/>
        </div>

        <button @click="onSubmit" class="btn btn-primary" :disabled="!origin">
          <icon name="map-signs"/>
          {{$t('buttons.save')}}
        </button>
      </div>

      <div class="col">
        <div class="card">
          <mo-tree-view multiple v-model="destination"
                        class="card-body" v-if="origin"/>
          <div class="card-body" v-else>
            <p class="card-text">
              Vælg en enhed til venstre for at vise og ændre hvilke
              enheder der svarer til den andre steder i
              organisationen.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MoTreeView from '@/components/MoTreeView/MoTreeView'
import 'vue-awesome/icons/map-signs'
import { mapGetters } from 'vuex'
import OrganisationMapper from './_components/OrganisationMapper'
import store from './_store'
import main_store from '@/store'
const STORE_KEY = '$_organisationMapper'

main_store.registerModule(STORE_KEY, store)

export default {
  name: 'OrganisationMapperModule',
  components: {
    MoTreeView
  },
  computed: {
    origin: {
      get () {
        return this.$store.getters[`${STORE_KEY}/origin`]
      },
      set (val) {
        this.$store.commit(`${STORE_KEY}/SET_ORIGIN`, val)
      }
    },

    destination: {
      get () {
        return this.$store.getters[`${STORE_KEY}/destination`]
      },
      set (val) {
        this.$store.commit(`${STORE_KEY}/SET_DESTINATION`, val)
        return this.$store.getters[`${STORE_KEY}/destination`]
      }
    }
  },

  watch: {
    origin (newVal) {
      this.$store.dispatch(`${STORE_KEY}/GET_ORGANISATION_MAPPINGS`)
    },
    destination (newVal) {
      console.log('destination changed!')
    }
  },

  methods: {
    onSubmit () {
      this.$store.dispatch(`${STORE_KEY}/MAP_ORGANISATIONS`)
    }
  }
}
</script>

<style scoped>
  .mapper-column {
    min-height: 10em;
    margin-bottom: 1em;
  }
</style>
