import Vue from 'vue'
import AddressSearchTemplate from '@/components/AddressSearchTemplate'

let Constructor

let item = {
  UUID_EnhedsAdresse: '0a3f50c6-b76b-32b8-e044-0003ba298018',
  postdistrikt: 'Aars',
  postnr: '9600',
  vejnavn: 'Testrupvej 203, Testrup, 9600 Aars'
}

describe('AddressSearchTemplate.vue', () => {
  beforeEach(function () {
    // Extend the component to get the constructor, which we can then initialize directly.
    Constructor = Vue.extend(AddressSearchTemplate)
  })

  it('should render an address', () => {
    const vm = new Constructor({
      propsData: {
        item: item
      }
    }).$mount()

    expect(vm.$el.querySelector('label').textContent)
    .to.equal(item.vejnavn)
  })
})
