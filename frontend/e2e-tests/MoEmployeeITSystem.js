let moment = require('moment')

import { Selector } from 'testcafe'
import VueSelector from 'testcafe-vue-selectors'
import { baseURL } from './support'

fixture('MoEmployeeITSystem')
  .page(`${baseURL}/medarbejder/1ce40e25-6238-4202-9e93-526b348ec745`)

test('Read IT System', async t => {
  await t
    .click(VueSelector('employee-detail-tabs bTabButtonHelper').withText('IT'))
    .expect(VueSelector('mo-link').filter('.itsystem-name').innerText)
    .contains('Active Directory')
    .expect(VueSelector('mo-link').filter('.user_key').innerText)
    .contains('chef@ballerup.dk')
})
