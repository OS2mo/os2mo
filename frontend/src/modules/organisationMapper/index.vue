<template>
  <div>
    <h1>{{$t('shared.organisation_mapping')}}</h1>

    <div class="row">
      <div class="col">
        <div class="card">
          <mo-tree-view class="card-body origin" v-model="origin"/>
        </div>

        <button @click="onSubmit" class="btn btn-primary btn-submit"
                :disabled="!valid">
          <icon name="map-signs"/>
          {{$t('buttons.save')}}
        </button>
      </div>

      <div class="col">
        <div class="card">
          <mo-tree-view multiple v-model="destination" :disabled-unit="origin"
                        class="card-body destination" v-if="origin"/>
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
import isEqualTo from 'lodash.isequal'
import MoTreeView from '@/components/MoTreeView/MoTreeView'
import 'vue-awesome/icons/map-signs'
import { mapGetters } from 'vuex'
import store from './_store'
import main_store from '@/store'

main_store.registerModule('organisationMapper', store)

export default {
  name: 'OrganisationMapperModule',
  components: {
    MoTreeView
  },
  computed: {
    origin: {
      get () {
        return this.$store.getters['organisationMapper/origin']
      },
      set (val) {
        this.$store.commit('organisationMapper/SET_ORIGIN', val)
      }
    },

    destination: {
      get () {
        return this.$store.getters['organisationMapper/destination']
      },
      set (val) {
        this.$store.commit('organisationMapper/SET_DESTINATION', val)
        return this.$store.getters['organisationMapper/destination']
      }
    },

    valid () {
      return this.origin && !isEqualTo(this.original_destination, this.destination)
    },

    ...mapGetters({
      original_destination: 'organisationMapper/original_destination'
    })
  },

  watch: {
    origin (newVal) {
      this.$store.dispatch('organisationMapper/GET_ORGANISATION_MAPPINGS')
    }
  },

  methods: {
    onSubmit () {
      this.$store.dispatch('organisationMapper/MAP_ORGANISATIONS')
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
