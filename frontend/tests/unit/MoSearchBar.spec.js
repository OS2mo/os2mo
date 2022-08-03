// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import VeeValidate from "vee-validate"
import moment from "moment"
import Search from "@/api/Search"
import { AtDate } from "@/store/actions/atDate"
import MoSearchBar from "@/components/MoSearchBar/MoSearchBar.vue"
import i18n from "@/i18n.js"
import MoAutocomplete from "@/components/MoAutocomplete/MoAutocomplete.vue"
import Autocomplete from "@trevoreyre/autocomplete-vue"

jest.mock("@/api/Search")

describe("MoSearchBar.vue", () => {
  let wrapper, store

  beforeEach(() => {
    // Mock Vue '$t' translation function
    const $t = (msg) => msg

    // Mock Vue $route (this is read by the `MoSearchBar` component)
    const $route = { name: "Organisation" }

    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VeeValidate)

    // Set up mock Vuex store
    store = new Vuex.Store()
    store.dispatch = jest.fn()
    store.replaceState({ organisation: { uuid: "1234" } })

    // Mock resolved value of `Search.organisations` (actual value does not matter)
    Search.organisations.mockResolvedValue([])

    wrapper = mount(MoSearchBar, {
      store,
      localVue,
      i18n,
      mocks: { $t, $route },
    })
  })

  it("should dispatch `AtDate.SET` when the `atDate` property is changed", async () => {
    const now = new Date(),
      nowFormatted = moment(now).format("YYYY-MM-DD")
    await wrapper.setData({ atDate: now })
    expect(store.dispatch).toHaveBeenCalledWith(AtDate.actions.SET, nowFormatted)
  })

  it("should use `atDate` in `updateItems`", async () => {
    // Set `atDate` to a known value
    let now = new Date(),
      nowFormatted = moment(now).format("YYYY-MM-DD")
    await wrapper.setData({ atDate: now })

    // Search query passed to `Search.organisations`
    const query = "my query"

    await wrapper.vm.updateItems(query)
    expect(Search.organisations).toHaveBeenCalledWith(
      store.state.organisation.uuid,
      query,
      nowFormatted
    )
  })

  it("should call the search API when search input is entered", async () => {
    const query = "my query"

    // Pretend to type query into autocomplete widget
    const component = wrapper.findComponent(MoAutocomplete).findComponent(Autocomplete)
    component.setData({ defaultValue: query })

    // Assert that search function is called with query as input
    expect(Search.organisations).toHaveBeenCalledWith(
      store.state.organisation.uuid,
      query,
      expect.anything()
    )
  })
})
