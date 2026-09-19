require('@babel/register')({
  presets: [['@babel/preset-react', { runtime: 'automatic' }]],
  extensions: ['.jsx', '.js']
})

try {
  require('./src/pages/HotelBudget.jsx')
  console.log("HotelBudget.jsx parsed successfully")
} catch(e) {
  console.log(e)
}
