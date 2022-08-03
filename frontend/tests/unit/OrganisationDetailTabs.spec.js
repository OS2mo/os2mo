// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import OrganisationDetailTabs from "@/views/organisation/OrganisationDetailTabs.vue"

describe("OrganisationDetailTabs.vue", () => {
  const dateA = "2020-01-01",
    dateB = "2020-12-31"
  const spyLoadContent = jest.spyOn(OrganisationDetailTabs.methods, "loadContent")

  let mountComponent = () => {
    // Mock Vue '$t' translation function
    const $t = (msg) => msg

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
      },
    })

    // Mock 'uuid' and 'orgUnitInfo' properties
    const propsData = {
      uuid: "uuid",
      orgUnitInfo: {
        user_settings: {
          org_unit: {
            show_roles: true,
            show_kle: true,
            show_time_planning: true,
            show_level: true,
            show_primary_engagement: true,
            show_primary_association: true,
          },
        },
      },
    }

    const wrapper = mount(OrganisationDetailTabs, {
      store,
      localVue,
      propsData: propsData,
      mocks: { $t, $route },
      computed: {
        route: () => {
          return $route
        },
      },
    })

    return {
      wrapper: wrapper,
      propsData: propsData,
    }
  }

  it("should read the date when the component is mounted", async () => {
    // This relies on the initial 'atDate' being set to `dateA` in the mock
    // Vuex store
    const env = mountComponent()
    expect(env.wrapper.vm._atDate).toEqual(dateA)
  })

  it("should call `loadContent` for past, present and future on date changes", async () => {
    const expectedDetail = "org_unit"
    const env = mountComponent()
    env.wrapper.vm.$options.watch.atDate.call(env.wrapper.vm, dateB)

    let showEvents = env.wrapper.emitted().show
    expect(showEvents.length).toEqual(3)

    for (var validity of ["past", "present", "future"]) {
      expect(spyLoadContent).toHaveBeenCalledWith(expectedDetail, validity)
      // Find 'show' events emitted from `loadContent`
      var matchingShowEvents = []
      for (var eventList of showEvents) {
        for (var event of eventList) {
          if (event.validity == validity) {
            matchingShowEvents.push(event)
          }
        }
      }
      // Check each emitted 'show' event (one for past, present and future)
      expect(matchingShowEvents.length).toEqual(1)
      expect(matchingShowEvents[0].uuid).toEqual(env.propsData.uuid)
      expect(matchingShowEvents[0].detail).toEqual(expectedDetail)
      expect(matchingShowEvents[0].validity).toEqual(validity)
      expect(matchingShowEvents[0].atDate).toEqual(dateB)
    }
  })
})
