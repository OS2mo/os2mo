// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { createLocalVue, mount } from "@vue/test-utils"
import VeeValidate from "vee-validate"
import DateTimePicker from "vuejs-datepicker"
import MoInputDate from "@/components/MoInput/MoInputDate.vue"
import i18n from "@/i18n.js"

describe("MoInputDate.vue", () => {
  let mountComponent = (propsData) => {
    // Set up local Vue object
    const localVue = createLocalVue()
    localVue.use(VeeValidate)

    const wrapper = mount(MoInputDate, {
      localVue,
      i18n,
      propsData: propsData,
    })

    return { wrapper: wrapper }
  }

  it("should read the `clearButton` property", async () => {
    const env = mountComponent({ clearButton: false })
    const childComponent = env.wrapper.findComponent(DateTimePicker)
    expect(childComponent.vm.clearButton).toEqual(false)
  })
})
