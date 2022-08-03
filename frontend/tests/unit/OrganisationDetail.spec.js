// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import OrganisationDetail from "@/views/organisation/OrganisationDetail.vue"

describe("OrganisationDetail.vue", () => {
  const dateA = "2020-01-01",
    dateB = "2020-12-31"
  const spyLoadContent = jest.spyOn(OrganisationDetail.methods, "loadContent")

  let mountComponent = () => {
    // Mock Vue '$t' translation functions
    const $t = (msg) => msg
    const $tc = (msg) => msg

    // Mock Vue $route
    const $route = { params: { name: "name", uuid: "uuid" } }

    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)

    // Set up mock Vuex store
    const store = new Vuex.Store({
      getters: {
        "atDate/GET": () => {
          return dateA
        },
        "conf/GET_CONF_DB": () => {
          return { show_org_unit_button: true }
        },
        "log/getWorkLog": () => [],
        "organisationUnit/GET_ORG_UNIT": () => undefined,
      },
      actions: {
        "organisationUnit/SET_ORG_UNIT": () => undefined,
      },
    })

    const wrapper = mount(OrganisationDetail, {
      store,
      localVue,
      mocks: { $t, $tc, $route },
      computed: {
        route: () => {
          return $route
        },
      },
    })

    wrapper.setData({ latestEvent: {} })

    return { wrapper: wrapper }
  }

  it("should read the date when the component is mounted", async () => {
    // This relies on the initial 'atDate' being set to `dateA` in the mock
    // Vuex store
    const env = mountComponent()
    expect(env.wrapper.vm._atDate).toEqual(dateA)
  })

  it("should call `loadContent` when the date is changed", async () => {
    const env = mountComponent()
    env.wrapper.vm.$options.watch.atDate.call(env.wrapper.vm, dateB)
    expect(env.wrapper.vm._atDate).toEqual(dateB)
    expect(spyLoadContent).toHaveBeenCalled()
  })
})
