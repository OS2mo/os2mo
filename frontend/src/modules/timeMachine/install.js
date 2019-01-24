import MoNavbar from '@/api/MoNavbar.js'
import 'vue-awesome/icons/history'

const ShortcutButton = () => import('./_components/ShortcutButton.vue')

MoNavbar.addShortcut(ShortcutButton, 200)
