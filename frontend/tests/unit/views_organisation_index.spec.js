// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import VeeValidate from "vee-validate"
import VueSplit from "vue-split-panel"
import VueShortKey from "vue-shortkey"
import IndexView from "@/views/organisation/index"
import Organisation from "@/api/Organisation"
import OrganisationUnit from "@/api/OrganisationUnit"

jest.mock("@/api/Organisation")
jest.mock("@/api/OrganisationUnit")

describe("views/organisation/index.vue", () => {
  const facetClasses = [
    { uuid: "1", name: "First class" },
    { uuid: "2", name: "Second class" },
  ]
  const expectedDropdownItems = [
    { value: null, text: "shared.entire_organisation" },
    { value: "1", text: "First class" },
    { value: "2", text: "Second class" },
  ]

  Organisation.getChildren.mockResolvedValue([])
  OrganisationUnit.getAncestorTree.mockResolvedValue([])

  // Mock `document.getElementById`
  const spyGetElementById = (id) => {
    return { style: { height: 0 } }
  }
  Object.defineProperty(global.document, "getElementById", { value: spyGetElementById })

  let mountComponent = () => {
    // Mock Vue '$t' translation functions
    const $t = (msg) => msg
    const $tc = (msg) => msg

    // Mock Vue $route and $router
    const $route = { params: { name: "name", uuid: "uuid" } }
    const $router = []

    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VeeValidate)
    localVue.use(VueSplit)
    localVue.use(VueShortKey)

    // Set up mock Vuex store
    const store = new Vuex.Store({
      getters: {
        "atDate/GET": () => "2020-01-01",
        "organisationUnit/GET_ORG_UNIT": () => "uuid",
        "facet/GET_FACET": () => {
          return (key) => {
            return { classes: facetClasses }
          }
        },
      },
      actions: {
        "organisation/SET_ORGANISATION": jest.fn(),
      },
    })

    const wrapper = mount(IndexView, {
      store,
      localVue,
      mocks: { $t, $tc, $route, $router },
      computed: {
        route: () => {
          return $route
        },
      },
    })

    return {
      wrapper: wrapper,
      expectedDropdownItems: expectedDropdownItems,
    }
  }

  it("should fetch the facet `org_unit_hierarchy` when mounted", async () => {
    const env = mountComponent()
    expect(env.wrapper.vm.options).toEqual(env.expectedDropdownItems)
  })

  it("should reset the route when the `orgUnitHierarchy` filter is changed", async () => {
    const env = mountComponent()
    env.wrapper.vm.$options.watch.orgUnitHierarchy.call(env.wrapper.vm, "class-uuid")
    expect(env.wrapper.vm.$router).toEqual([{ name: "OrganisationLandingPage" }])
  })
})
