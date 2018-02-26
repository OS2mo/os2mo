// import axios from 'axios'
import moxios from 'moxios'
import sinon from 'sinon'
import HTTP from '@/api/HttpCommon'
import Property from '@/api/Property'

describe('Property.js', () => {
  beforeEach(() => {
    moxios.install(HTTP)
  })

  afterEach(() => {
    moxios.uninstall(HTTP)
  })

  it('returns the api call', (done) => {
    // Match against an exact URL value
    moxios.stubRequest('/org-unit/type', {
      status: 200,
      responseText: 'hello'
    })

    let onFulfilled = sinon.spy()
    Property.getOrganisationUnitTypes().then(onFulfilled)

    moxios.wait(function () {
      // expect(onFulfilled.getCall(0).args[0].data).to.be('hello')
      done()
    })
  })
})
