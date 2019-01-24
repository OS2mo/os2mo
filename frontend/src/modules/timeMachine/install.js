import MoNavbar from '@/api/MoNavbar.js'

const ShortcutButton = () => import('./_components/ShortcutButton.vue')

MoNavbar.addShortcut(ShortcutButton, 200)
