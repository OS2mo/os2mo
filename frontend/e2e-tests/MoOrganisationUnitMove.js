import { Selector } from 'testcafe'
import { baseURL, reset } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoOrganisationUnitMove')
  .afterEach(reset)
  .page(`${baseURL}/organisation/fb816fdf-bef3-4d49-89cb-3d3bde3e5b54`)

const dialog = Selector('#orgUnitMove')

const unitInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const parentInput = dialog.find('.parentUnit input[data-vv-as="Angiv ny overenhed"]')

const fromInput = dialog.find('.moveDate input.form-control')

const tree = VueSelector('mo-tree-view')

let currentUnitName = Selector('.orgunit .orgunit-name')

test('Workflow: move unit', async t => {
  let today = moment()

  await t
    .expect(currentUnitName.visible)
    .ok()
    .expect(currentUnitName.innerText)
    .eql('Social og sundhed')
    .expect(tree.find('.selected').exists)
    .ok()
    .expect(tree.getVue(({ computed }) => computed.contents))
    .eql({
      'Hjørring': [
        '> Borgmesterens Afdeling',
        '> Skole og Børn',
        '=+= Social og sundhed =+=',
        '> Teknik og Miljø'
      ]
    })

    .hover('#mo-workflow', { offsetX: 10, offsetY: 90 })
    .click('.btn-unit-move')

    .expect(dialog.exists).ok('Opened dialog')

    .click(unitInput)
    .click(dialog.find('.currentUnit .tree-node')
      .withText('Hjørring').find('.tree-arrow'))
    .click(dialog.find('.currentUnit .tree-anchor')
      .withText('Social og sundhed'))
    .expect(dialog.find('.currentUnit input[data-vv-as="Angiv enhed"]').value)
    .eql('Social og sundhed')

    .click(parentInput)
    .click(dialog.find('.parentUnit .tree-node')
      .withText('Hjørring')
      .find('.tree-arrow'))
    .click(dialog.find('.parentUnit .tree-anchor')
      .withText('Borgmesterens Afdeling'))
    .expect(dialog.find('.parentUnit input[data-vv-as="Angiv ny overenhed"]').value)
    .eql('Borgmesterens Afdeling')

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
      /Organisationsenheden med UUID [-0-9a-f]* er blevet flyttet/
    )

    .expect(tree.find('.selected').exists)
    .ok()
    .expect(tree.getVue(({ computed }) => computed.contents))
    .eql({
      'Hjørring': [
        {
          'Borgmesterens Afdeling': [
            'Budget og Planlægning',
            'Byudvikling',
            'Erhverv',
            'HR og organisation',
            'IT-Support',
            '=+= Social og sundhed =+='
          ]
        },
        '> Skole og Børn',
        '> Teknik og Miljø'
      ]
    })

    .expect(Selector('.orgunit-name').textContent)
    .eql('Social og sundhed')
    .expect(Selector('.orgunit-location').textContent, { timeout: 1500 })
    .eql('Hjørring/Borgmesterens Afdeling')
    .expect(Selector('.detail-present ul.parent-name').textContent)
    .match(/Borgmesterens Afdeling/)

    .click(Selector('.detail-past .card-header'))
    .expect(Selector('.detail-past ul.parent-name').textContent)
    .match(/Hjørring/)

    .click(Selector('.detail-future .card-header'))
    .expect(Selector('.detail-past ul.parent-name').textContent)
    .match(/Hjørring/)
})
