// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import MoTreeView from "@/components/MoTreeView/MoTreeView.vue"

describe("MoTreeView.vue", () => {
  const orgUnitUuid = "uuid"
  const dateA = "2020-01-01",
    dateB = "2020-12-31"
  const validity = { from: "2021-01-01", to: null }
  const spyUpdateTree = jest.spyOn(MoTreeView.methods, "updateTree")

  let mountComponent = (ancestorTreeValue, topLevelChildrenValue) => {
    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)

    // Set up mock Vuex store
    const store = new Vuex.Store({
      getters: {
        "atDate/GET": () => dateA,
      },
    })

    const get_ancestor_tree = jest.fn().mockResolvedValue(ancestorTreeValue || [])
    const get_toplevel_children = jest
      .fn()
      .mockResolvedValue(topLevelChildrenValue || [])

    const wrapper = mount(MoTreeView, {
      store,
      localVue,
      propsData: {
        value: orgUnitUuid,
        get_store_uuid: () => undefined,
        get_ancestor_tree: get_ancestor_tree,
        get_toplevel_children: get_toplevel_children,
      },
    })

    return {
      wrapper: wrapper,
      get_ancestor_tree: get_ancestor_tree,
      get_toplevel_children: get_toplevel_children,
    }
  }

  it("should update the tree when the component is mounted", async () => {
    // This relies on the initial 'atDate' being set to `dateA` in the mock
    // Vuex store
    const env = mountComponent()
    expect(env.wrapper.vm._atDate).toEqual(dateA)
    expect(spyUpdateTree).toHaveBeenCalled()
    expect(env.get_ancestor_tree).toHaveBeenCalledWith(orgUnitUuid, dateA)
  })

  it("should update the tree when the date is changed", async () => {
    const env = mountComponent()
    env.wrapper.vm.$options.watch.atDate.call(env.wrapper.vm, dateB)
    expect(env.wrapper.vm._atDate).toEqual(dateB)
    expect(spyUpdateTree).toHaveBeenCalled()
    expect(env.get_ancestor_tree).toHaveBeenCalledWith(orgUnitUuid, dateB)
  })

  it("should update the tree when `updateValidity` is called", async () => {
    const env = mountComponent()
    env.wrapper.vm.updateValidity(validity)
    expect(env.wrapper.vm._atDate).toEqual(validity.from)
    expect(spyUpdateTree).toHaveBeenCalled()
    expect(env.get_ancestor_tree).toHaveBeenCalledWith(orgUnitUuid, validity.from)
  })

  it("should not fetch top-level children if ancestor tree exists", async () => {
    const env = mountComponent(
      // Mock resolved value of `get_ancestor_tree` to be a non-empty array
      ["foobar"]
    )
    expect(spyUpdateTree).toHaveBeenCalled()
    expect(env.get_ancestor_tree).toHaveBeenCalled()
    expect(env.get_toplevel_children).not.toHaveBeenCalled()
  })
})
