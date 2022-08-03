// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "@/api/HttpCommon"
import store from "@/store"
import { OrganisationUnit } from "@/store/actions/organisationUnit"

jest.mock("@/api/HttpCommon")

describe("OrganisationUnit.js: action: SET_ORG_UNIT", () => {
  const spyServiceGet = jest.spyOn(Service, "get")

  let payload = (atDate) => {
    return {
      uuid: "<uuid>",
      atDate: atDate,
    }
  }

  beforeEach(() => {
    Service.get.mockResolvedValue([])
  })

  it("should include `at` parameter in the service URL", async () => {
    store.dispatch(OrganisationUnit.actions.SET_ORG_UNIT, payload("2020-01-01"))
    expect(spyServiceGet).toBeCalledWith("/ou/<uuid>/?at=2020-01-01")
  })
})
