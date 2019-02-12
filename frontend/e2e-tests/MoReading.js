import VueSelector from 'testcafe-vue-selectors'
import { baseURL } from './support'

fixture('MoEmployeeITSystem')
  .page(`${baseURL}/medarbejder/75878240-2999-4bb4-b9c0-665f1553ef25`)

test('Read IT System', async t => {
  await t
    .click(VueSelector('employee-detail-tabs bTabButtonHelper').withText('IT'))
    .expect(VueSelector('mo-link').filter('.itsystem-name').exists)
    .ok()
    .expect(VueSelector('mo-link').filter('.itsystem-name').innerText)
    .contains('Active Directory')
    .expect(VueSelector('mo-link').filter('.user_key').innerText)
    .contains('LineC')
})

fixture('MoOrganisationUnitITSystem')
  .page(`${baseURL}/organisation/97337de5-6096-41f9-921e-5bed7a140d85`)

// skip: test data lacks units with IT systems
test.skip('Read IT System', async t => {
  await t
    .click(VueSelector('organisation-detail-tabs bTabButtonHelper').withText('IT'))
    .expect(VueSelector('mo-link').filter('.itsystem-name').innerText)
    .contains('Lokal Rammearkitektur')
    .expect(VueSelector('mo-link').filter('.user_key').innerText)
    .contains('root')
})
