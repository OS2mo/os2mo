// SPDX-FileCopyrightText: 2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import Vuex from "vuex"
import Index from "@/modules/insight/index.vue"
import Service from "@/api/HttpCommon"

jest.mock("@/api/HttpCommon")

describe("index.vue", () => {
  let mountComponent = () => {
    // Mock Vue '$t' translation functions
    const $t = (msg) => msg
    const $tc = (msg) => msg

    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(Vuex)

    // Set up mock Vuex store
    const store = new Vuex.Store()

    const wrapper = mount(Index, {
      localVue,
      store,
      mocks: { $t, $tc },
    })

    return {
      wrapper: wrapper,
    }
  }

  const mockServiceGetValid = (url) => {
    if (url === "/insight/files") {
      return new Promise((resolve, reject) => {
        resolve({
          data: ["hest.json", "hund.json"],
        })
      })
    } else if (url === "/insight?q=all") {
      return new Promise((resolve, reject) => {
        resolve({
          data: [mockInsightData],
        })
      })
    } else {
      // For "/exports/" and new endpoints in the future
      return mockPromise()
    }
  }

  const mockServiceGetError = (url) => {
    if (url === "/insight/files") {
      return new Promise((resolve, reject) => {
        reject({
          response: {
            data: {
              error: true,
              description: "Directory does not exist.",
              status: 500,
              error_key: "E_DIR_NOT_FOUND",
              directory: "/app/backend/mora/queries/json_reports",
            },
          },
        })
      })
    } else if (url === "/insight?q=all") {
      return mockPromise()
    } else {
      // For "/exports/" and new endpoints in the future
      return mockPromise()
    }
  }

  it("should have the files and data from the /insight endpoints", async () => {
    Service.get = mockServiceGetValid

    const env = mountComponent()
    await env.wrapper.vm.update()

    expect(env.wrapper.vm.query_files).toEqual(["hest.json", "hund.json"])
    expect(env.wrapper.vm.query_data).toEqual([mockInsightData])
  })

  it("should show an error if endpoint return E_DIR_NOT_FOUND", async () => {
    Service.get = mockServiceGetError

    const env = mountComponent()
    // const spyHandleError = jest.spyOn(Index, 'handleError')
    await env.wrapper.vm.update()

    // console.log(env.wrapper.vm.query_files);
    // console.log(env.wrapper.emitted());
    // expect(env.wrapper.emitted().error[1]).toEqual('E_DIR_NOT_FOUND')

    // expect(spyWindow).toHaveBeenCalled()
    // expect(spyHandleError).toHaveBeenCalled()
  })
})

const mockInsightData = [
  {
    title: "SD and P No.",
    schema: {
      fields: [
        {
          name: "index",
          type: "integer",
        },
        {
          name: "root",
          type: "string",
        },
      ],
    },
    data: [
      {
        index: 0,
        root: "Kolding Kommune",
        org: null,
        "sub org": null,
        "2xsub org": null,
        "3xsub org": null,
        Adresse: "Castenskjoldsvej 2, 2., 6000 Kolding",
        "P-nummer": "1866728518",
      },
      {
        index: 1,
        root: "Kolding Kommune",
        org: "Borgmesterens Afdeling",
        "sub org": null,
        "2xsub org": null,
        "3xsub org": null,
        Adresse: "Baggesensvej 14, 6000 Kolding",
        "P-nummer": "1880516418",
      },
    ],
  },
]

const mockPromise = () => {
  return new Promise((resolve, reject) => {
    resolve({
      data: [],
    })
  })
}
