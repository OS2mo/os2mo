import MoNavbar from '@/api/MoNavbar.js'
import 'vue-awesome/icons/question-circle'

const ShortcutButton = () => import('./ShortcutButton.vue')

MoNavbar.addShortcut(ShortcutButton, 300)
