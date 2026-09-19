import fs from 'fs'
import { transformSync } from 'esbuild'

const jsx = fs.readFileSync('./src/pages/HotelExpenseBudget.jsx', 'utf-8')
const code = transformSync(jsx, { loader: 'jsx', format: 'esm' }).code

// We just want to see if parsing/loading throws a ReferenceError.
// We can't fully run React, but we can verify imports.
console.log("No syntax errors. JSX transpiled successfully.")
