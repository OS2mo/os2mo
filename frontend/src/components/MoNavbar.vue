SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
    <router-link
      :class="
        show_custom_logo != '' ? 'logo ' + show_custom_logo + ' col-1' : 'logo col-1'
      "
      :to="{ name: 'Landing' }"
    >
    </router-link>

    <button
      class="navbar-toggler"
      type="button"
      data-toggle="collapse"
      data-target="#navbarSupportedContent"
      aria-controls="navbarSupportedContent"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'Employee' }">{{
            $t("navbar.employee")
          }}</router-link>
        </li>

        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'Organisation' }">{{
            $t("navbar.organisation")
          }}</router-link>
        </li>

        <b-dropdown
          v-if="navlinks.length"
          v-bind:text="$t('navbar.navlinks.title')"
          variant="primary"
        >
          <b-dropdown-item
            v-for="(navlink, index) in navlinks"
            :key="index"
            :href="navlink.href"
            target="_blank"
          >
            {{ navlink.text }}
          </b-dropdown-item>
        </b-dropdown>
      </ul>

      <mo-organisation-picker reset-route class="ml-auto mr-auto" />

      <mo-search-bar class="ml-auto mr-auto" />

      <component
        v-for="(shortcut, index) in shortcuts"
        :key="index"
        :is="shortcut.template"
      />

      <mo-locale-picker />

      <b-dropdown variant="primary">
        <template slot="button-content">
          <icon name="user" />
          {{ username }}
        </template>
        <b-dropdown-item @click="logout()">
          <icon name="sign-out-alt" />
          {{ $t("common.sign_out") }}
        </b-dropdown-item>
      </b-dropdown>
    </div>
  </nav>
</template>

<script>
import { Validator } from "vee-validate"
import MoNavbar from "@/api/MoNavbar"
import MoLocalePicker from "@/components/MoLocalePicker.vue"
import MoSearchBar from "@/components/MoSearchBar/MoSearchBar"
import MoOrganisationPicker from "@/components/MoPicker/MoOrganisationPicker"
import bDropdown from "bootstrap-vue/es/components/dropdown/dropdown"
import bDropdownItem from "bootstrap-vue/es/components/dropdown/dropdown-item"
import { Conf } from "@/store/actions/conf"
import keycloak from "@/main"

export default {
  components: {
    MoSearchBar,
    MoOrganisationPicker,
    MoLocalePicker,
    "b-dropdown": bDropdown,
    "b-dropdown-item": bDropdownItem,
  },

  data() {
    return {
      user: {},
      username: "N/A",
      shortcuts: [],
      navlinks: [],
    }
  },

  created() {
    this.username = keycloak.idTokenParsed
      ? keycloak.idTokenParsed.preferred_username
      : "Nobody"
    this.shortcuts = MoNavbar.getShortcuts()

    this.$store.dispatch(Conf.actions.SET_NAVLINKS).then((response) => {
      this.navlinks = this.$store.getters[Conf.getters.GET_NAVLINKS]
    })
  },

  computed: {
    show_custom_logo() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      return conf.show_custom_logo != "" ? "custom_logo_" + conf.show_custom_logo : ""
    },
  },

  methods: {
    /**
     * Logout and redirect back to frontpage
     */
    logout() {
      let vm = this
      keycloak.logout({ redirectUri: window.location.origin })
    },
  },
}
</script>

<style scoped>
.nav-item .nav-link {
  color: #e5e0de;
  border-bottom: 3px solid transparent;
}
.nav-item .nav-link:hover,
.nav-item .nav-link.router-link-active {
  border-bottom: 3px solid #e5e0de;
}

.b-dropdown {
  padding: 0 0.25rem;
}
</style>
