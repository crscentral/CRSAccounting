import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../../lib/supabaseClient'
import { useAuth } from '../../lib/AuthContext'

export default function TallyMasterCreate() {
  const { activeCompany, activeProduct } = useAuth()
  const navigate = useNavigate()
  
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [type, setType] = useState('Revenue')
  const [subtype, setSubtype] = useState('')
  const [description, setDescription] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  
  const [activeField, setActiveField] = useState('name')

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        navigate('/tally-mode')
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [navigate])

  const handleInputKeyDown = async (e, field) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (field === 'name') setActiveField('code')
      else if (field === 'code') setActiveField('type')
      else if (field === 'type') setActiveField('subtype')
      else if (field === 'subtype') setActiveField('description')
      else if (field === 'description') {
        // Save
        if (!name.trim()) {
          setMessage('Name is required')
          return
        }
        setSaving(true)
        setMessage('Saving...')
        const payload = {
          company_id: activeCompany.id,
          product: activeProduct,
          name: name.trim(),
          code: code.trim(),
          type,
          subtype: subtype.trim(),
          description: description.trim()
        }
        const { error } = await supabase.from('accounts').insert(payload)
        setSaving(false)
        if (error) {
          setMessage('Error: ' + error.message)
        } else {
          setMessage('Ledger created successfully!')
          setName('')
          setCode('')
          setSubtype('')
          setDescription('')
          setActiveField('name')
          setTimeout(() => setMessage(''), 2000)
        }
      }
    }
  }

  return (
    <div className="tally-voucher-container">
      <div className="tally-voucher-main">
        <div className="tally-voucher-header">
          <span>Ledger Alteration / Creation</span>
          <span className="text-blue-900">Master</span>
        </div>
        
        <div className="bg-white border border-slate-300 p-8 max-w-2xl mx-auto w-full shadow-sm">
          <div className="font-bold text-lg mb-6 border-b pb-2 text-center text-slate-800">Ledger Creation</div>
          
          <div className="grid grid-cols-[120px_1fr] gap-4 mb-4 items-center">
            <div className="font-semibold text-right pr-2">Name</div>
            <div>
              <input 
                autoFocus={activeField === 'name'}
                className="tally-input font-bold border-b border-dashed border-slate-400 focus:bg-[#e6f2ff]"
                value={name}
                onChange={e => setName(e.target.value)}
                onKeyDown={e => handleInputKeyDown(e, 'name')}
                onFocus={() => setActiveField('name')}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-[120px_1fr] gap-4 mb-4 items-center">
            <div className="font-semibold text-right pr-2">Code (Alias)</div>
            <div>
              <input 
                autoFocus={activeField === 'code'}
                className="tally-input font-bold border-b border-dashed border-slate-400 focus:bg-[#e6f2ff]"
                value={code}
                onChange={e => setCode(e.target.value)}
                onKeyDown={e => handleInputKeyDown(e, 'code')}
                onFocus={() => setActiveField('code')}
              />
            </div>
          </div>

          <div className="grid grid-cols-[120px_1fr] gap-4 mb-4 items-center">
            <div className="font-semibold text-right pr-2">Under (Type)</div>
            <div>
              <select 
                autoFocus={activeField === 'type'}
                className="tally-input font-bold border-b border-dashed border-slate-400 focus:bg-[#e6f2ff] bg-transparent"
                value={type}
                onChange={e => setType(e.target.value)}
                onKeyDown={e => handleInputKeyDown(e, 'type')}
                onFocus={() => setActiveField('type')}
              >
                {['Revenue', 'Expense', 'Asset', 'Liability', 'Equity'].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-[120px_1fr] gap-4 mb-4 items-center">
            <div className="font-semibold text-right pr-2">Subtype</div>
            <div>
              <input 
                autoFocus={activeField === 'subtype'}
                className="tally-input font-bold border-b border-dashed border-slate-400 focus:bg-[#e6f2ff]"
                value={subtype}
                onChange={e => setSubtype(e.target.value)}
                onKeyDown={e => handleInputKeyDown(e, 'subtype')}
                onFocus={() => setActiveField('subtype')}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-[120px_1fr] gap-4 mb-4 items-center">
            <div className="font-semibold text-right pr-2">Description</div>
            <div>
              <input 
                autoFocus={activeField === 'description'}
                className="tally-input font-bold border-b border-dashed border-slate-400 focus:bg-[#e6f2ff]"
                value={description}
                onChange={e => setDescription(e.target.value)}
                onKeyDown={e => handleInputKeyDown(e, 'description')}
                onFocus={() => setActiveField('description')}
                placeholder="Press Enter to Save"
              />
            </div>
          </div>

          {message && (
            <div className="mt-6 text-center font-bold text-blue-800 bg-blue-50 py-2 border border-blue-200">
              {message}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
