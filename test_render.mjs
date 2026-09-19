import fs from 'fs'
import { transformSync } from 'esbuild'

const jsx = fs.readFileSync('./src/pages/HotelExpenseBudget.jsx', 'utf-8')
const code = transformSync(jsx, { loader: 'jsx', format: 'esm' }).code
fs.writeFileSync('./dist/test_cmp.mjs', code)
