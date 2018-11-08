import VueSelector from 'testcafe-vue-selectors'
import { baseURL } from './support'

fixture('Organisation unit IT system test')
  .page(`${baseURL}/organisation/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4`)

test('Read IT System', async t => {
  await t
    .click(VueSelector('organisation-detail-tabs bTabButtonHelper').withText('IT'))
    .expect(VueSelector('mo-link').filter('.itsystem-name').innerText)
    .contains('Lokal Rammearkitektur')
    .expect(VueSelector('mo-link').filter('.user_key').innerText)
    .contains('root')
})
