import Vue from 'vue'
import PageNotFound from '@/components/PageNotFound'

let Constructor

xdescribe('PageNotFound.vue', () => {
  beforeEach(function () {
    // Extend the component to get the constructor, which we can then initialize directly.
    Constructor = Vue.extend(PageNotFound)
  })

  it('should render correctly', () => {
    const vm = new Constructor().$mount()

    expect(vm.$el.querySelector('h1').textContent)
    .to.equal('Siden blev ikke fundet')
  })
})
