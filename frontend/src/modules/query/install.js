import MoNavbar from '@/api/MoNavbar.js'
import 'vue-awesome/icons/exchange-alt'

const ShortcutButton = () => import('./ShortcutButton.vue')

MoNavbar.addShortcut(ShortcutButton, 100)
