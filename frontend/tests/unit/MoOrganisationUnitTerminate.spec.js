// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import VeeValidate from "vee-validate"
import MoOrganisationUnitTerminate from "@/views/organisation/workflows/MoOrganisationUnitTerminate.vue"

describe("MoOrganisationUnitTerminate.vue", () => {
  let mountComponent = () => {
    // Mock Vue '$t' translation function
    const $t = (msg) => msg

    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VeeValidate)

    // Set up mock Vuex store
    const store = new Vuex.Store()
    store.dispatch = jest.fn()

    const wrapper = mount(MoOrganisationUnitTerminate, {
      store,
      localVue,
      mocks: { $t },
    })

    return {
      wrapper: wrapper,
      store: store,
      setDetailKey: "_organisationUnitTerminate/SET_DETAIL",
      mockEvent: {
        uuid: "uuid",
        detail: "org_unit",
        validity: "present",
        atDate: new Date(),
      },
    }
  }

  it("should use the current date when `terminate.from` is blank", async () => {
    const env = mountComponent()
    env.wrapper.vm.loadContent(env.mockEvent)
    expect(env.store.dispatch).toHaveBeenCalledWith(env.setDetailKey, env.mockEvent)
    expect(env.wrapper.vm.latestEvent).toEqual(env.mockEvent)
  })

  it("should use `terminate.from` when it is set", async () => {
    const env = mountComponent()
    const terminateFrom = new Date()
    const expectedEvent = { atDate: terminateFrom, ...env.mockEvent }
    env.wrapper.setData({ terminate: { from: terminateFrom } })
    env.wrapper.vm.loadContent(env.mockEvent)
    expect(env.store.dispatch).toHaveBeenCalledWith(env.setDetailKey, expectedEvent)
    expect(env.wrapper.vm.latestEvent).toEqual(expectedEvent)
  })
})
