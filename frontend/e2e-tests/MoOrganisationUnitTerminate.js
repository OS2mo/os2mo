import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('Organisation test')
  .page(`${baseURL}/organisation`)

const dialog = Selector('#orgUnitTerminate')

const parentInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const fromInput = dialog.find('.from-date input.form-control')

test('Workflow: terminate unit', async t => {
  let today = moment().add(1, 'days')

  await t
    .setTestSpeed(0.8)
    .hover('#mo-workflow', { offsetX: 10, offsetY: 130 })
    .click('.btn-unit-terminate')

    .expect(dialog.exists).ok('Opened dialog')

    .click(parentInput)
    .click(dialog.find('li .item .link-color').withText('Ballerup Idrætspark'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet afsluttet/
    )
})
