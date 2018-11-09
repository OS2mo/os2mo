import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('Organisation test')
  .page(`${baseURL}/organisation`)

const dialog = Selector('#orgUnitMove')

const unitInput = dialog.find('input[data-vv-as="Enhed"]')

const parentInput = dialog.find('.parentUnit input[data-vv-as="Enhed"]')

const fromInput = dialog.find('.moveDate input.form-control')

test('Workflow: move unit', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', {offsetX: 10, offsetY: 90})
    .click('.btn-unit-move')

    .expect(dialog.exists).ok('Opened dialog')

    .click(unitInput)
    .click(dialog.find('.currentUnit .tree-node')
           .withText('Ballerup Kommune').find('.tree-arrow'))
    .click(dialog.find('.currentUnit .tree-node')
           .withText('Ballerup Familiehus'))

    .click(parentInput)
    .click(dialog.find('.parentUnit .tree-node')
           .withText('Ballerup Kommune')
           .find('.tree-arrow'))
    .click(dialog.find('.parentUnit .tree-anchor')
           .withText('Ballerup Bibliotek'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog MoWorklog')
            .find('.alert').nth(-1).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet flyttet/
    )

    .expect(Selector('.orgunit-name').textContent)
    .eql('Ballerup Familiehus')
    .expect(Selector('.orgunit-location').textContent)
    .eql('Ballerup Kommune/Ballerup Bibliotek')
    .expect(Selector('.detail-present ul.parent-name').textContent)
    .match(/Ballerup Bibliotek/)

    .click(Selector('.detail-past .card-header'))
    .expect(Selector('.detail-past ul.parent-name').textContent)
    .match(/Ballerup Kommune/)

    .click(Selector('.detail-future .card-header'))
    .expect(Selector('.detail-past ul.parent-name').textContent)
    .match(/Ballerup Kommune/)
})
