import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoOrganisationUnitTerminate')
  .page(`${baseURL}/organisation`)

const createDialog = Selector('#orgUnitCreate')

const createTimeSelect = createDialog.find('select[data-vv-as="Tidsregistrering"]')
const createTimeOption = createTimeSelect.find('option')

const createUnitSelect = createDialog.find('select[data-vv-as="Enhedstype"]')
const createUnitOption = createUnitSelect.find('option')

const createAddressInput = createDialog.find('.v-autocomplete[data-vv-as="Adresse"]')
const createAddressItem = createAddressInput.find('.v-autocomplete-list-item label')

const createParentInput = createDialog.find('input[data-vv-as="Angiv overenhed"]')

const createFromInput = createDialog.find('.from-date input.form-control')

const dialog = Selector('#orgUnitTerminate')

const parentInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const fromInput = dialog.find('.from-date input.form-control')

test('Workflow: terminate org unit', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', { offsetX: 10, offsetY: 10 })
    .click('.btn-unit-create')

    .expect(createDialog.exists).ok('Opened dialog')

    .typeText(createDialog.find('input[data-vv-as="Navn"]'), 'Hjørring VM 2018')

    .click(createUnitSelect)
    .click(createUnitOption.withText('Fagligt center'))

    .click(createTimeSelect)
    .click(createTimeOption.withText('Tjenestetid'))

    .click(createParentInput)
    .click(createDialog.find('li.tree-node span.tree-anchor span'))

    .click(createFromInput)
    .hover(createDialog.find('.vdp-datepicker .day:not(.blank)'))
    .click(createDialog.find('.vdp-datepicker .day:not(.blank)'))
    .expect(createFromInput.value).eql(today.format('01-MM-YYYY'))

    .click(createAddressInput)
    .typeText(createAddressInput.find('input'), 'hjør')
    .expect(createAddressItem.withText('Hjørringgade').visible).ok()
    .pressKey('down enter')
    .expect(createAddressInput.find('input').value)
    .eql('Hjørringgade 1, 9850 Hirtshals')

    .typeText(createDialog.find('input[data-vv-as="Tlf"]'), '44772000')

    .click(createDialog.find('.btn-primary'))

    .expect(createDialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet oprettet/
    )

    .hover('#mo-workflow', { offsetX: 10, offsetY: 130 })
    .click('.btn-unit-terminate')

    .expect(dialog.exists).ok('Opened dialog')

    .click(parentInput)
    .click(dialog.find('.tree-node')
      .withText('Hjørring')
      .find('.tree-arrow'))
    .click(dialog.find('.tree-anchor').withText('VM 2018'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    // verify that the details render as expected
    .expect(dialog.find('.detail-present ul.name').withText('VM 2018').exists)
    .ok()

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet afsluttet/
    )
})
