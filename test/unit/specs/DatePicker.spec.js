import Vue from 'vue'
import DatePicker from '@/components/DatePicker'

let Constructor

describe('DatePicker.vue', () => {
  beforeEach(function () {
    // Extend the component to get the constructor, which we can then initialize directly.
    Constructor = Vue.extend(DatePicker)
  })

  xit('should render its default label', () => {
    const vm = new Constructor().$mount()
    expect(vm.$el.querySelector('label#date-label').textContent)
      .to.equal('Dato')
  })

  xit('should render a custom label', () => {
    let customLabel = 'Custom Label'

    const vm = new Constructor({
      propsData: {
        label: customLabel
      }
    }).$mount()

    expect(vm.$el.querySelector('label#date-label').textContent)
      .to.equal(customLabel)
  })
})
