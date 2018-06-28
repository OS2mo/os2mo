import { Selector } from 'testcafe'
import { baseURL } from './support'

fixture('Organisation test')
  .page(`${baseURL}/organisation/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4`)

const dialog = Selector('#orgUnitCreate')

const unitSelect = dialog.find('select[data-vv-as="Enhedstype"]')
const unitOption = unitSelect.find('option')

const addressInput = dialog.find('.v-autocomplete[data-vv-as="Postadresse"]')
const addressItem = addressInput.find('.v-autocomplete-list-item label')

const parentInput = dialog.find('.v-autocomplete[data-vv-as="Enhed"]')
const parentItem = parentInput.find('.v-autocomplete-list-item label')

test('MoOrganisationUnitCreate', async t => {
  await t
    .hover('#mo-workflow', {offsetX: 10, offsetY: 10})
    .click('.btn-unit-create')

    .expect(dialog.exists).ok('Opened dialog')

    .typeText('input[data-vv-as="Navn"]', 'Ballerup Fredagsbar')

    .click('.from-date input')
    .click('.vdp-datepicker .day:not(.blank)')

    .click(unitSelect)
    .click(unitOption.withText('Supportcenter'))

    .click(parentInput)
    .typeText(parentInput.find('input'), 'Bal')
    .pressKey('down enter')
    // .click(parentItem.withText('Bib'), {offsetX: 5, offsetY: 5, speed: 0.5})
    .expect(parentInput.find('input').value).eql('Ballerup Bibliotek')

    .click(addressInput)
    .typeText(addressInput.find('input'), 'Hold-An')
    .pressKey('down enter')
    // .click(addressItem.withText('Hold-An Vej 12, 2750 Ballerup').find('label'))
    .expect(addressInput.find('input').value).contains('Hold-An Vej')

    .typeText('input[data-vv-as="Telefonnummer"]', '44772000')
    .pressKey('enter')

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#orgUnitCreate').exists).notOk()
})

