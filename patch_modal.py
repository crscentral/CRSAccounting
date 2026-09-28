with open('src/components/PurchaseInvoiceFormModal.jsx', 'r') as f:
    content = f.read()

# Replace useAuth destructuring
old_use_auth = "  const { activeRole } = useAuth()"
new_use_auth = "  const { activeRole, user } = useAuth()"
content = content.replace(old_use_auth, new_use_auth)

# Hide the upload field for non-superadmin
old_field = """            <Field label="Upload Supplier Invoice (PDF, JPG, PNG)">
              <label className="flex items-center gap-2 border border-dashed border-slate-300 rounded-lg px-3 py-2 text-sm cursor-pointer text-slate-500 hover:border-navy-400">
                <Upload size={15} />
                {uploading ? 'Uploading…' : attachmentUrl ? (<><span className="mr-2">File attached ✓</span><a href={attachmentUrl} target="_blank" rel="noopener noreferrer" className="text-navy-600 hover:underline text-xs font-medium" onClick={e => e.stopPropagation()}>Preview</a></>) : 'Choose File'}
                <input type="file" accept="application/pdf,image/jpeg,image/png,image/jpg" className="hidden" onChange={e => e.target.files[0] && handleFileUpload(e.target.files[0])} />
              </label>
            </Field>"""

new_field = """            {user?.email === 'crscentral.rm@gmail.com' && (
              <Field label="Upload Supplier Invoice (PDF, JPG, PNG)">
                <label className="flex items-center gap-2 border border-dashed border-slate-300 rounded-lg px-3 py-2 text-sm cursor-pointer text-slate-500 hover:border-navy-400">
                  <Upload size={15} />
                  {uploading ? 'Uploading…' : attachmentUrl ? (<><span className="mr-2">File attached ✓</span><a href={attachmentUrl} target="_blank" rel="noopener noreferrer" className="text-navy-600 hover:underline text-xs font-medium" onClick={e => e.stopPropagation()}>Preview</a></>) : 'Choose File'}
                  <input type="file" accept="application/pdf,image/jpeg,image/png,image/jpg" className="hidden" onChange={e => e.target.files[0] && handleFileUpload(e.target.files[0])} />
                </label>
              </Field>
            )}"""

content = content.replace(old_field, new_field)

with open('src/components/PurchaseInvoiceFormModal.jsx', 'w') as f:
    f.write(content)
