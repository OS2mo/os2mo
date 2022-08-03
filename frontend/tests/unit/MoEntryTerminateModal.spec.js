// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import VeeValidate from "vee-validate"
import Service from "@/api/HttpCommon"
import { EventBus, Events } from "@/EventBus"
import MoEntryTerminateModal from "@/components/MoEntryTerminateModal.vue"

jest.mock("@/api/HttpCommon")

describe("MoEntryTerminateModal.vue", () => {
  let defaultPropsData = {
    content: {
      validity: { from: "2021-01-01", to: null },
      parent: { uuid: "parent-uuid" },
    },
    type: "org_unit",
  }

  const event = { preventDefault: () => {} }

  Service.post.mockResolvedValue([])

  let mountComponent = (propsData) => {
    // Mock Vue '$t' translation functions
    const $t = (msg) => msg
    const $tc = (msg) => msg

    // Mock Vue router
    const $router = { push: jest.fn() }

    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VeeValidate)

    // Mock Vuex store
    const store = new Vuex.Store({
      mutations: {
        "log/newWorkLog": () => undefined,
      },
    })

    const wrapper = mount(MoEntryTerminateModal, {
      localVue,
      store,
      mocks: { $t, $tc, $router },
      propsData: propsData,
    })

    return { wrapper: wrapper }
  }

  it('should not show the "to date" when terminating an org unit', async () => {
    const env = mountComponent(defaultPropsData)
    expect(env.wrapper.vm.showToDate).toEqual(false)
  })

  it('should call the "/details/terminate" API upon termination', async () => {
    const env = mountComponent(defaultPropsData)
    const spyServicePost = jest.spyOn(Service, "post")
    const expectedUrl = "/details/terminate"
    const expectedPayload = {
      type: defaultPropsData.type,
      validity: defaultPropsData.content.validity,
      uuid: undefined,
    }
    await env.wrapper.vm.terminate(event) // invoke event handler
    expect(spyServicePost).toHaveBeenCalledWith(expectedUrl, expectedPayload)
  })

  it("should navigate to the parent OU upon termination", async () => {
    const env = mountComponent(defaultPropsData)
    const expectedRoute = {
      name: "OrganisationDetail",
      params: { uuid: "parent-uuid" },
    }
    await env.wrapper.vm.terminate(event) // invoke event handler
    expect(env.wrapper.vm.$router.push).toHaveBeenCalledWith(expectedRoute)
  })

  it("should update the org tree view upon termination", async () => {
    const env = mountComponent(defaultPropsData)
    const spyEventBusEmit = jest.spyOn(EventBus, "$emit")
    await env.wrapper.vm.terminate(event) // invoke event handler
    expect(spyEventBusEmit).toHaveBeenCalledWith(Events.UPDATE_TREE_VIEW)
  })
})
