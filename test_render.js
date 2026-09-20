import { renderToString } from 'react-dom/server'
import React from 'react'
import HotelBudget from './src/pages/HotelBudget.jsx'

// Mock the AuthContext and other dependencies
jest.mock('./src/lib/AuthContext', () => ({
  useAuth: () => ({ activeCompany: { id: '123', name: 'Test' }, activeProduct: 'hotel', can: () => true })
}))

// We need babel to compile JSX on the fly
