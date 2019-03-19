import VueSelector from 'testcafe-vue-selectors'
import { baseURL, reset } from './support'

fixture('MoOrganisationUnitITSystem')
  .afterEach(reset)
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
