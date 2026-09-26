import re

with open('src/pages/TallyMode/TallyGateway.jsx', 'r') as f:
    content = f.read()

# Add imports
content = content.replace(
    "import { useNavigate } from 'react-router-dom'",
    "import { useNavigate } from 'react-router-dom'\nimport { useAuth } from '../../lib/AuthContext'\nimport { useCurrencyAndPeriod } from '../../lib/useCurrencyAndPeriod'"
)

# Use Auth
content = content.replace(
    "  const navigate = useNavigate()",
    "  const navigate = useNavigate()\n  const { activeCompany } = useAuth()\n  const cp = useCurrencyAndPeriod()"
)

# Change container layout to be a flex row taking full width
old_container = """  return (
    <div className="tally-gateway-container">
      <div className="tally-gateway-menu">"""

new_container = """  return (
    <div className="flex flex-1 w-full bg-[#fdf5e6]">
      {/* Left Pane: Company Info */}
      <div className="flex-1 flex flex-col border-r border-[#c0b3a0] p-4 text-slate-800">
        <div className="flex justify-between border-b border-[#c0b3a0] pb-2 mb-4 font-bold text-[13px]">
          <div>
            <div className="text-[#800000]">Current Period</div>
            <div>{cp.range.from} to {cp.range.to}</div>
          </div>
          <div className="text-right">
            <div className="text-[#800000]">Current Date</div>
            <div>{new Date().toISOString().slice(0, 10)}</div>
          </div>
        </div>
        
        <div className="flex justify-between font-bold text-[13px] border-b border-[#c0b3a0] pb-2 text-[#800000]">
          <div>Name of Company</div>
          <div>Date of Last Entry</div>
        </div>
        
        <div className="flex justify-between mt-2 font-bold text-[14px]">
          <div>{activeCompany?.name || 'Loading...'}</div>
          <div className="font-normal text-[12px] italic">No Vouchers Entered</div>
        </div>
      </div>

      {/* Right Pane: Gateway Menu */}
      <div className="w-[400px] flex flex-col items-center justify-center p-8 bg-[var(--tally-blue)]">
        <div className="tally-gateway-menu">"""
content = content.replace(old_container, new_container)

content = content.replace(
    """      </div>
    </div>
  )""",
    """      </div>
      </div>
    </div>
  )"""
)

with open('src/pages/TallyMode/TallyGateway.jsx', 'w') as f:
    f.write(content)
