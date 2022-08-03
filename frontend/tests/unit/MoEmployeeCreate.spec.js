// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import VueRouter from "vue-router"
import VeeValidate from "vee-validate"
import Service from "@/api/HttpCommon"
import MoEmployeeCreate from "@/views/employee/MoEmployeeWorkflows/MoEmployeeCreate.vue"
import MoCpr from "@/components/MoCpr"
import i18n from "@/i18n.js"

jest.mock("@/api/HttpCommon")

describe("MoEmployeeCreate.vue", () => {
  const spyServicePost = jest.spyOn(Service, "post")
  Service.post.mockResolvedValue({ data: "employee-uuid" })

  let mountComponent = () => {
    // Mock MO organisation
    const organisation = { name: "organisation name" }

    // Mock Vue '$t' translation functions
    const $t = (msg) => msg
    const $tc = (msg) => msg

    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    localVue.use(VeeValidate)

    // Set up mock Vuex store
    const store = new Vuex.Store({
      getters: {
        "conf/GET_CONF_DB": () => {
          return { show_seniority: true }
        },
        "organisation/GET_ORGANISATION": () => {
          return organisation
        },
      },
    })
    jest.spyOn(store, "dispatch")

    // Set up mock Vue router
    const router = new VueRouter()

    const wrapper = mount(MoEmployeeCreate, {
      localVue,
      store,
      router,
      i18n,
      mocks: { $t, $tc },
    })

    return {
      wrapper: wrapper,
      store: store,
      organisation: organisation,
    }
  }

  it('should not call "create employee" API when an empty form is submitted', async () => {
    const env = mountComponent()

    // Submit form data (empty)
    const form = env.wrapper.find("form")
    await form.trigger("submit")

    // Assert we did not dispatch on the Vuex store, and we did not POST to the
    // "create employee" API.
    expect(env.wrapper.vm.$store.dispatch).not.toHaveBeenCalled()
    expect(spyServicePost).not.toHaveBeenCalled()
  })

  it('should call "create employee" API when only a CPR number is given', async () => {
    const env = mountComponent()

    const expectedApiUrl = "/e/create"
    const expectedPayload = {
      cpr_no: "0101012222",
      details: [],
      name: undefined,
      nickname_givenname: undefined,
      nickname_surname: undefined,
      org: env.organisation,
      seniority: null,
    }

    // Fill out CPR number (the only required field on form)
    const cpr = env.wrapper.findComponent(MoCpr)
    cpr.setData({
      result: {
        cpr_no: expectedPayload["cpr_no"],
        name: "Firstname Lastname",
      },
    })
    await env.wrapper.vm.$validator.validateAll()

    // Submit form data
    const form = env.wrapper.find("form")
    await form.trigger("submit")

    // Assert that we dispatched on the Vuex store, and we POSTed the expected
    // payload to the "create employee" API.
    expect(env.wrapper.vm.$store.dispatch).toHaveBeenCalled()
    expect(spyServicePost).toHaveBeenCalledWith(expectedApiUrl, expectedPayload)
  })
})
