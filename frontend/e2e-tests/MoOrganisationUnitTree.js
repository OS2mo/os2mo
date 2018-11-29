import { Selector } from 'testcafe'
import VueSelector from 'testcafe-vue-selectors'
import { baseURL } from './support'

const dialog = Selector('#orgUnitTerminate')

const trees = new Map([
  ['', '> Hjørring'],
  ['97337de5-6096-41f9-921e-5bed7a140d85', '> =+= Hjørring =+='],
  ['be7bb9e5-b298-4019-b0fd-ce80c8f97934', {
    'Hjørring': [
      '> Borgmesterens Afdeling',
      '> Skole og Børn',
      'Social og sundhed',
      '> =+= Teknik og Miljø =+='
    ]
  }]
])

let tree = Selector('.orgunit-tree')
let treeNode = tree.find('.tree-node')
let treeAnchor = treeNode.find('.tree-anchor')
let rootNode = treeNode.withAttribute('data-id', '97337de5-6096-41f9-921e-5bed7a140d85')
let selected = treeNode.filter('.selected')

let currentUnitName = Selector('.orgunit .orgunit-name')

fixture('MoOrganisationUnitTree')

for (const [selection, contents] of trees.entries()) {
  test
    .page`${baseURL}/organisation/${selection}`
  (`Load of '${selection}'`, async t => {
    await t
      .wait(500)
      .expect(tree.exists)
      .ok()
      .expect(rootNode.exists)
      .ok()
      .expect(VueSelector('mo-tree-view').exists)
      .ok()
      .expect(selected.exists)
      .eql(selection.length > 0, { timeout: 1500 })
      .expect(VueSelector('mo-tree-view')
        .getVue(({ computed }) => computed.contents))
      .eql(contents)
  })
}

test
  .page`${baseURL}/organisation/`
('Path changes', async t => {
  await t
    .expect(treeNode.exists)
    .ok()
    .expect(rootNode.exists)
    .ok()
    .expect(currentUnitName.exists)
    .notOk()
    .click(rootNode)
    .expect(currentUnitName.innerText)
    .eql('Hjørring')
    .expect(rootNode.find('.tree-children').exists)
    .notOk()
    .click(rootNode.find('.tree-arrow'))
    .expect(rootNode.find('.tree-children').exists)
    .ok()

    .click(treeAnchor.withText('Social og sundhed'))
    .expect(currentUnitName.innerText)
    .eql('Social og sundhed')
    .expect(t.eval(() => location.pathname))
    .eql('/organisation/fb816fdf-bef3-4d49-89cb-3d3bde3e5b54')
})
