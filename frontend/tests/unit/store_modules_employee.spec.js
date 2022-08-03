// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "@/api/HttpCommon"
import store from "@/store"
import { Employee } from "@/store/actions/employee"

jest.mock("@/api/HttpCommon")

describe("employee.js: action: SET_DETAIL", () => {
  const spyServiceGet = jest.spyOn(Service, "get")

  let payload = (atDate, extra, validity) => {
    return {
      uuid: "<uuid>",
      detail: "employee",
      atDate: atDate,
      extra: extra,
      validity: validity || "present",
    }
  }

  beforeEach(() => {
    Service.get.mockResolvedValue([])
  })

  it("should include `at` parameter in the service URL", async () => {
    store.dispatch(Employee.actions.SET_DETAIL, payload("2020-01-01"))
    expect(spyServiceGet).toBeCalledWith(
      "/e/<uuid>/details/employee?validity=present&at=2020-01-01"
    )
  })

  it("should use the validity given as a parameter in the service URL", async () => {
    const future = payload("2020-01-01", undefined, "future")
    store.dispatch(Employee.actions.SET_DETAIL, future)
    expect(spyServiceGet).toBeCalledWith(
      "/e/<uuid>/details/employee?validity=future&at=2020-01-01"
    )
  })

  it("should include extra parameters in the service URL, if given", async () => {
    store.dispatch(Employee.actions.SET_DETAIL, payload("2020-01-01", { foo: "bar" }))
    expect(spyServiceGet).toBeCalledWith(
      "/e/<uuid>/details/employee?validity=present&at=2020-01-01&foo=bar"
    )
  })
})
