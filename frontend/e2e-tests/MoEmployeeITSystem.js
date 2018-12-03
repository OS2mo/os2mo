import VueSelector from 'testcafe-vue-selectors'
import { baseURL } from './support'

fixture('MoEmployeeITSystem')
  .page(`${baseURL}/medarbejder/75878240-2999-4bb4-b9c0-665f1553ef25`)

test('Read IT System', async t => {
  await t
    .click(VueSelector('employee-detail-tabs bTabButtonHelper').withText('IT'))
    .expect(VueSelector('mo-link').filter('.itsystem-name').innerText)
    .contains('Active Directory')
    .expect(VueSelector('mo-link').filter('.user_key').innerText)
    .contains('LineC')
})
