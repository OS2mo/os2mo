// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import MoOrgTreeView from "@/components/MoTreeView/MoOrgTreeView.vue"
import Organisation from "@/api/Organisation"
import OrganisationUnit from "@/api/OrganisationUnit"

jest.mock("@/api/Organisation")
jest.mock("@/api/OrganisationUnit")

describe("MoOrgTreeView.vue", () => {
  const orgUnitUuid = "uuid"
  const dateA = "2020-01-01"
  const spyGetAncestorTree = jest.spyOn(OrganisationUnit, "getAncestorTree")

  Organisation.getChildren.mockResolvedValue([])
  OrganisationUnit.getAncestorTree.mockResolvedValue([])

  let mountComponent = () => {
    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)

    // Set up mock Vuex store
    const store = new Vuex.Store({
      getters: {
        "atDate/GET": () => dateA,
      },
    })

    const wrapper = mount(MoOrgTreeView, {
      store,
      localVue,
      propsData: {
        value: orgUnitUuid,
        get_store_uuid: () => undefined,
      },
    })

    return {
      wrapper: wrapper,
    }
  }

  it("should use `_extraQueryArgs` when `setFilter` is called", async () => {
    const env = mountComponent()
    env.wrapper.vm.setFilter("class-uuid")
    expect(env.wrapper.vm._extraQueryArgs).toEqual({ org_unit_hierarchy: "class-uuid" })
    expect(spyGetAncestorTree).toHaveBeenCalledWith(
      orgUnitUuid,
      dateA,
      env.wrapper.vm._extraQueryArgs
    )
  })
})
