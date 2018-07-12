import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('Organisation test')
  .page(`${baseURL}/organisation`)

const dialog = Selector('#orgUnitRename')

const parentInput = dialog.find('.v-autocomplete[data-vv-as="Enhed"]')
const parentItem = parentInput.find('.v-autocomplete-list-item label')

const fromInput = dialog.find('.from-date input.form-control')

test('Workflow: rename unit', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)

    .hover('#mo-workflow', {offsetX: 10, offsetY: 50})
    .click('.btn-unit-rename')

    .expect(dialog.exists).ok('Opened dialog')

    .click(parentInput)
    .typeText(parentInput.find('input'), 'bib')
    .expect(parentItem.withText('Ballerup Bibliotek').visible).ok()
    .pressKey('down enter')
    .expect(parentInput.find('input').value).eql('Ballerup Bibliotek')

    .typeText(dialog.find('input[data-vv-as="Nyt navn"]'), 'Ballerup Hovedbibliotek')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#orgUnitRename').exists).notOk()

    // Running the test second time
    .hover('#mo-workflow', {offsetX: 10, offsetY: 50})
    .click('.btn-unit-rename')

    .expect(dialog.exists).ok('Opened dialog')

    .click(parentInput)
    .typeText(parentInput.find('input'), 'hoved')
    .expect(parentItem.withText('Ballerup Hovedbibliotek').visible).ok()
    .pressKey('down enter')
    .expect(parentInput.find('input').value).eql('Ballerup Hovedbibliotek')

    .typeText(dialog.find('input[data-vv-as="Nyt navn"]'), 'Ballerup Bibliotek')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#orgUnitRename').exists).notOk()
})
