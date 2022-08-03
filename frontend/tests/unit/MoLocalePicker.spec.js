// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import FlagIcon from "vue-flag-icon"
import i18n from "@/i18n.js"
import MoLocalePicker from "@/components/MoLocalePicker.vue"

describe("MoLocalePicker.vue", () => {
  const spySetLocale = jest.spyOn(MoLocalePicker.methods, "setLocale")

  let mountComponent = () => {
    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(FlagIcon)

    const wrapper = mount(MoLocalePicker, { i18n, localVue })
    return { wrapper: wrapper }
  }

  it("should read the locale when the component is mounted", async () => {
    const env = mountComponent()
    expect(env.wrapper.vm.currentLocale).toEqual("da")
    expect(spySetLocale).toHaveBeenCalledWith("da")
  })

  it("should update the locale when the user makes a choice", async () => {
    const env = mountComponent()
    env.wrapper.vm.$options.watch.currentLocale.call(env.wrapper.vm, "en")
    expect(spySetLocale).toHaveBeenCalledWith("en")
  })
})
