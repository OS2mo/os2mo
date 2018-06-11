import { Selector } from 'testcafe'

fixture('Organisation test')
  .page('http://localhost:8080/organisation/')

const unitSelect = Selector('select[data-vv-as="Enhedstype"]')
const unitOption = unitSelect.find('option')
const searchInput = Selector('.v-autocomplete[data-vv-as="Postadresse"]')
const searchItem = searchInput.find('.v-autocomplete-list')

test('MoOrganisationUnitCreate', async t => {
  await t
    .hover('#mo-workflow', {offsetX: 10, offsetY: 10})
    .click('#orgUnitCreate')
    .setTestSpeed(0.3)
    .typeText('input[data-vv-as="Navn"]', 'Ballerup Fredagsbar')
    .click(unitSelect)
    .click(unitOption.withText('Supportcenter'))
    .click(searchInput)
    .typeText('.v-autocomplete[data-vv-as="Postadresse"]', 'Balle')
    .click(searchItem.withText('Ballerup Byvej 300, 1., 2750 Ballerup'))
    .click('button[type="submit"]')
})
