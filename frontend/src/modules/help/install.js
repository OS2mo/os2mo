import MoNavbar from '@/api/MoNavbar.js'

const ShortcutButton = () => import('./ShortcutButton.vue')

MoNavbar.addShortcut(ShortcutButton, 300)
