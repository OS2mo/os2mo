import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('Employee test')
  .page(`${baseURL}/medarbejder/liste`)

const dialog = Selector('#employeeMoveMany')

const fromInput = dialog.find('input.form-control')

const parentFromInput = dialog.find('.from-unit .v-autocomplete[data-vv-as="Enhed"]')
const parentFromItem = parentFromInput.find('.from-unit .v-autocomplete-list-item label')

const parentToInput = dialog.find('.to-unit .v-autocomplete[data-vv-as="Enhed"]')
const parentToItem = parentToInput.find('.to-unit .v-autocomplete-list-item label')

const checkboxInput = dialog.find('.checkbox-employee[data-vv-as="checkbox"]')

test('Workflow: moveMany employee', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)
    .hover('#mo-workflow', {offsetX: 10, offsetY: 140})
    .click('.btn-employee-moveMany')

    .expect(dialog.exists).ok('Opened dialog')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(parentFromInput)
    .typeText(parentFromInput.find('input'), 'fam')
    .expect(parentFromItem.withText('Ballerup Familiehus').visible).ok()
    .pressKey('down enter')
    .expect(parentFromInput.find('input').value).eql('Ballerup Familiehus')

    .click(parentToInput)
    .typeText(parentToInput.find('input'), 'kom')
    .expect(parentToItem.withText('Ballerup Kommune').visible).ok()
    .pressKey('down enter')
    .expect(parentToInput.find('input').value).eql('Ballerup Kommune')

    .click(checkboxInput)

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#orgUnitRename').exists).notOk()
})
