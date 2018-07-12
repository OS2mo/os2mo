import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('Organisation test')
  .page(`${baseURL}/organisation`)

const dialog = Selector('#orgUnitMove')

const unitInput = dialog.find('.v-autocomplete[data-vv-as="Enhed"]')
const unitItem = unitInput.find('.v-autocomplete-list-item label')

const parentInput = dialog.find('.parentUnit .v-autocomplete[data-vv-as="Enhed"]')
const parentItem = parentInput.find('.parentUnit .v-autocomplete-list-item label')

const fromInput = dialog.find('.moveDate input.form-control')

test('Workflow: move unit', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)

    .hover('#mo-workflow', {offsetX: 10, offsetY: 90})
    .click('.btn-unit-move')

    .expect(dialog.exists).ok('Opened dialog')

    .click(unitInput)
    .typeText(unitInput.find('input'), 'vm 2018')
    .expect(unitItem.withText('Ballerup VM 2018').visible).ok()
    .pressKey('down enter')
    .expect(unitInput.find('input').value).eql('Ballerup VM 2018')

    .click(parentInput)
    .typeText(parentInput.find('input'), 'idræt')
    .expect(parentItem.withText('Ballerup Idrætspark').visible).ok()
    .pressKey('down enter')
    .expect(parentInput.find('input').value).eql('Ballerup Idrætspark')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#orgUnitCreate').exists).notOk()

    // Running the test second time
    .hover('#mo-workflow', {offsetX: 10, offsetY: 90})
    .click('.btn-unit-move')

    .expect(dialog.exists).ok('Opened dialog')

    .click(unitInput)
    .typeText(unitInput.find('input'), 'vm 2018')
    .expect(unitItem.withText('Ballerup VM 2018').visible).ok()
    .pressKey('down enter')
    .expect(unitInput.find('input').value).eql('Ballerup VM 2018')

    .click(parentInput)
    .typeText(parentInput.find('input'), 'fam')
    .expect(parentItem.withText('Ballerup Familiehus').visible).ok()
    .pressKey('down enter')
    .expect(parentInput.find('input').value).eql('Ballerup Familiehus')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#orgUnitCreate').exists).notOk()
})
