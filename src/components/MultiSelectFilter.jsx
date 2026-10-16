import { useState, useRef, useEffect, useMemo } from 'react'
import { ChevronDown, Search, X, Check } from 'lucide-react'

export default function MultiSelectFilter({
  placeholder = 'Select...',
  options = [],
  selectedValues = [],
  onChangeSelected,
  searchValue = '',
  onSearchChange,
  counts = {},
  title = 'Options',
  inputRef,
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [localSearch, setLocalSearch] = useState('')
  const containerRef = useRef(null)
  const searchInputRef = useRef(null)

  // Sync external ref if passed
  useEffect(() => {
    if (inputRef) {
      inputRef.current = {
        focus: () => {
          setIsOpen(true)
          setTimeout(() => {
            if (searchInputRef.current) searchInputRef.current.focus()
          }, 50)
        },
      }
    }
  }, [inputRef])

  // Close dropdown on outside click
  useEffect(() => {
    if (!isOpen) return
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  // Filter options based on local search input
  const filteredOptions = useMemo(() => {
    const q = localSearch.toLowerCase().trim()
    if (!q) return options
    return options.filter(opt => String(opt || '').toLowerCase().includes(q))
  }, [options, localSearch])

  function toggleOption(opt) {
    if (selectedValues.includes(opt)) {
      onChangeSelected(selectedValues.filter(v => v !== opt))
    } else {
      onChangeSelected([...selectedValues, opt])
    }
  }

  function handleSelectAll() {
    // If some filtered options are not selected, select all filtered options
    const allFilteredSelected = filteredOptions.every(opt => selectedValues.includes(opt))
    if (allFilteredSelected) {
      // Unselect all filtered options
      onChangeSelected(selectedValues.filter(v => !filteredOptions.includes(v)))
    } else {
      // Add all filtered options
      const combined = Array.from(new Set([...selectedValues, ...filteredOptions]))
      onChangeSelected(combined)
    }
  }

  function handleClearAll(e) {
    if (e) e.stopPropagation()
    onChangeSelected([])
    if (onSearchChange) onSearchChange('')
  }

  const hasSelections = selectedValues.length > 0
  const hasTextSearch = Boolean(searchValue && searchValue.trim())

  return (
    <div ref={containerRef} className="relative w-full">
      {/* Trigger Box */}
      <div
        onClick={() => {
          setIsOpen(prev => !prev)
          if (!isOpen) {
            setTimeout(() => {
              if (searchInputRef.current) searchInputRef.current.focus()
            }, 50)
          }
        }}
        className={`w-full text-xs min-h-[28px] px-2 py-1 bg-white border rounded cursor-pointer select-none flex items-center justify-between gap-1 transition-colors ${
          isOpen
            ? 'border-navy-500 ring-1 ring-navy-500'
            : hasSelections || hasTextSearch
            ? 'border-navy-400 bg-navy-50/20 text-navy-900 font-medium'
            : 'border-slate-300 hover:border-slate-400 text-slate-500 font-normal'
        }`}
        title={hasSelections ? selectedValues.join(', ') : placeholder}
      >
        <div className="truncate flex items-center gap-1.5 flex-1 min-w-0">
          {hasSelections ? (
            selectedValues.length === 1 ? (
              <span className="truncate font-medium text-slate-800">{selectedValues[0]}</span>
            ) : (
              <span className="inline-flex items-center gap-1 font-semibold text-navy-700 bg-navy-100/80 px-1.5 py-0.5 rounded text-[11px] whitespace-nowrap">
                {selectedValues.length} selected
              </span>
            )
          ) : hasTextSearch ? (
            <span className="truncate text-slate-800 font-medium">"{searchValue}"</span>
          ) : (
            <span className="truncate text-slate-400">{placeholder}</span>
          )}
        </div>

        <div className="flex items-center gap-1 shrink-0 text-slate-400">
          {(hasSelections || hasTextSearch) && (
            <button
              type="button"
              onClick={handleClearAll}
              className="p-0.5 hover:text-red-600 rounded"
              title="Clear selection"
            >
              <X size={11} />
            </button>
          )}
          <ChevronDown size={12} className={`transition-transform duration-150 ${isOpen ? 'rotate-180 text-navy-600' : ''}`} />
        </div>
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-1 z-50 bg-white border border-slate-200 rounded-lg shadow-xl min-w-[240px] max-w-[320px] p-2 text-xs">
          {/* Search box inside dropdown */}
          <div className="relative mb-2">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              ref={searchInputRef}
              type="text"
              value={localSearch}
              onChange={e => {
                setLocalSearch(e.target.value)
                if (onSearchChange) onSearchChange(e.target.value)
              }}
              placeholder={`Search ${title.toLowerCase()}...`}
              className="w-full pl-7 pr-6 py-1 bg-slate-50 border border-slate-200 rounded text-xs focus:outline-none focus:ring-1 focus:ring-navy-500 focus:bg-white text-slate-800"
            />
            {localSearch && (
              <button
                type="button"
                onClick={() => {
                  setLocalSearch('')
                  if (onSearchChange) onSearchChange('')
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X size={11} />
              </button>
            )}
          </div>

          {/* Quick Actions Header */}
          <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100 text-[11px] text-slate-500">
            <span>
              {selectedValues.length > 0 ? (
                <strong className="text-navy-700">{selectedValues.length}</strong>
              ) : (
                '0'
              )}{' '}
              of {options.length} selected
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleSelectAll}
                className="text-navy-600 hover:text-navy-800 font-medium hover:underline"
              >
                {filteredOptions.length > 0 && filteredOptions.every(opt => selectedValues.includes(opt))
                  ? 'Deselect All'
                  : 'Select All'}
              </button>
              {selectedValues.length > 0 && (
                <>
                  <span className="text-slate-300">|</span>
                  <button
                    type="button"
                    onClick={handleClearAll}
                    className="text-red-600 hover:text-red-700 font-medium hover:underline"
                  >
                    Clear
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Options List */}
          <div className="max-h-52 overflow-y-auto space-y-0.5 divide-y divide-slate-50">
            {filteredOptions.length === 0 ? (
              <div className="text-center py-4 text-slate-400 text-xs">
                No {title.toLowerCase()} found
              </div>
            ) : (
              filteredOptions.map(opt => {
                const isChecked = selectedValues.includes(opt)
                return (
                  <label
                    key={opt}
                    className={`flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer select-none transition-colors ${
                      isChecked ? 'bg-navy-50/70 text-navy-900 font-medium' : 'hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleOption(opt)}
                      className="rounded border-slate-300 text-navy-600 focus:ring-navy-500 h-3.5 w-3.5"
                    />
                    <span className="truncate flex-1 text-xs">{opt}</span>
                    {counts[opt] !== undefined && (
                      <span className="text-[10px] text-slate-400 bg-slate-100 px-1.5 py-0.2 rounded-full font-normal">
                        {counts[opt]}
                      </span>
                    )}
                  </label>
                )
              })
            )}
          </div>

          {/* Bottom Bar with Done Button */}
          <div className="pt-2 mt-1.5 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[10px] text-slate-400">
              {hasSelections ? 'Filtering applied live' : 'Select one or more'}
            </span>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="text-xs bg-navy-600 hover:bg-navy-700 text-white font-medium px-2.5 py-1 rounded"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
