import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('Organisation test')
  .page(`${baseURL}/organisation/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4`)

const dialog = Selector('#orgUnitCreate')

const unitSelect = dialog.find('select[data-vv-as="Enhedstype"]')
const unitOption = unitSelect.find('option')

const addressInput = dialog.find('.v-autocomplete[data-vv-as="Postadresse"]')
const addressItem = addressInput.find('.v-autocomplete-list-item label')

const parentInput = dialog.find('.v-autocomplete[data-vv-as="Enhed"]')
const parentItem = parentInput.find('.v-autocomplete-list-item label')

const fromInput = dialog.find('.from-date input.form-control')

const newDate = dialog.find('.btn-link')
const newDateInput = dialog.find('.address-date .from-date input.form-control')

test('Workflow: create unit', async t => {
  let today = moment()

  // Some notes:
  //
  // You may notice that we have a few 'expects' waiting for an
  // autocomplete to be visible. They exist to ensure that the
  // autocomplete is properly rendered prior to attempting to select
  // an item. This can occur when TestCafe runs at full speed.
  //
  // Likewise, not hovering over an item prior to clicking it can lead
  // to the click not having any effect.
  //
  // We do autocomplete selection using the keyboard. In order to make
  // this work, we use our own, fixed, version of 'v-autocomplete'
  // that suppresses form submit in these cases.
  //
  // I quite deliberately added a lot of expects that verify that e.g.
  // selecting something in a drop-down has the desired effect. This
  // ensures that we yield more helpful error messages should the test
  // fail, rather than merely failing at form submit.

  await t
    .setTestSpeed(0.8)
    .hover('#mo-workflow', {offsetX: 10, offsetY: 10})
    .click('.btn-unit-create')

    .expect(dialog.exists).ok('Opened dialog')

    .typeText(dialog.find('input[data-vv-as="Navn"]'), 'Ballerup VM 2018')

    .click(unitSelect)
    .click(unitOption.withText('Supportcenter'))

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

    .click(addressInput)
    .typeText(addressInput.find('input'), 'Hold-An')
    .expect(addressItem.withText('Hold-An Vej').visible).ok()
    .pressKey('down enter')
    .expect(addressInput.find('input').value).contains('Hold-An Vej')

    .click(newDate)
    .click(newDateInput)
    .hover(dialog.find('.address-date .from-date .vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.address-date .from-date .vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(newDateInput.value).eql(today.format('DD-MM-YYYY'))

    .typeText(dialog.find('input[data-vv-as="Telefonnummer"]'), '44772000')

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#orgUnitCreate').exists).notOk()

  // TODO: verify that the unit was actually created, somehow?
})
