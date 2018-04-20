import Vue from 'vue'
import ButtonWorkflow from '@/components/ButtonWorkflow'

let Constructor

xdescribe('ButtonWorkflow.vue', () => {
  beforeEach(function () {
    // Extend the component to get the constructor, which we can then initialize directly.
    Constructor = Vue.extend(ButtonWorkflow)
  })

  it('should render its default label', () => {
    const vm = new Constructor().$mount()
    expect(vm.$el.querySelector('label').textContent)
    .to.equal('New Workflow')
  })

  it('should render a custom label', () => {
    let customLabel = 'Custom Label'

    const vm = new Constructor({
      propsData: {
        label: customLabel
      }
    }).$mount()

    expect(vm.$el.querySelector('label').textContent)
    .to.equal(customLabel)
  })
})
