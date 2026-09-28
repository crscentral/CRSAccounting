import React, { useState } from 'react';
import { supabase } from '../lib/supabaseClient';
import { useAuth } from '../lib/AuthContext';
import { Download, Upload, AlertCircle, CheckCircle2 } from 'lucide-react';

const TABLES = [
  'accounts',
  'contacts',
  'hotel_settings',
  'hotel_expense_budget',
  'hotel_room_revenue_budget',
  'forecast_entries',
  'sales_invoices',
  'purchase_invoices',
  'payment_receipts',
  'hotel_expense_entries',
  'hotel_amc_contracts',
  'hotel_room_stats',
  'hotel_guest_invoices',
  'restaurant_daily_revenue',
  'ledger_entries'
];

const IMPORT_ORDER = [
  ['accounts', 'contacts', 'hotel_settings'],
  ['sales_invoices', 'purchase_invoices', 'hotel_amc_contracts', 'hotel_guest_invoices', 'restaurant_daily_revenue', 'hotel_expense_entries'],
  ['payment_receipts', 'ledger_entries', 'hotel_room_stats', 'hotel_expense_budget', 'hotel_room_revenue_budget', 'forecast_entries']
];

export default function BackupRestore() {
  const { activeCompany } = useAuth();
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('info'); // 'info', 'success', 'error'

  if (!activeCompany) return null;

  async function handleExport() {
    setExporting(true);
    setMessage('Exporting data...');
    setMessageType('info');
    try {
      const backup = {};
      for (const table of TABLES) {
        const { data, error } = await supabase
          .from(table)
          .select('*')
          .eq('company_id', activeCompany.id);
        
        if (error) throw error;
        backup[table] = data || [];
      }

      const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `crs-backup-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      setMessage('Export successful.');
      setMessageType('success');
    } catch (error) {
      console.error(error);
      setMessage(`Export failed: ${error.message}`);
      setMessageType('error');
    } finally {
      setExporting(false);
    }
  }

  async function handleImport(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setImporting(true);
    setMessage('Reading backup file...');
    setMessageType('info');

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const data = JSON.parse(e.target.result);
        
        // Verify company_id matches to prevent cross-company data pollution
        for (const table of TABLES) {
          if (data[table]) {
            const invalidRows = data[table].filter(row => row.company_id !== activeCompany.id);
            if (invalidRows.length > 0) {
              throw new Error(`Invalid company_id in table ${table}. You can only restore backups from this same company.`);
            }
          }
        }

        setMessage('Importing data. This may take a moment...');
        
        for (const group of IMPORT_ORDER) {
          for (const table of group) {
            if (data[table] && data[table].length > 0) {
              const { error } = await supabase.from(table).upsert(data[table]);
              if (error) throw error;
            }
          }
        }

        setMessage('Import successful. Refresh the page to see your restored data.');
        setMessageType('success');
      } catch (error) {
        console.error(error);
        setMessage(`Import failed: ${error.message}`);
        setMessageType('error');
      } finally {
        setImporting(false);
        event.target.value = ''; // Reset file input
      }
    };
    reader.onerror = () => {
      setMessage('Failed to read file.');
      setMessageType('error');
      setImporting(false);
    };
    reader.readAsText(file);
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 max-w-2xl">
      <h3 className="font-semibold text-slate-700 mb-4">Backup & Restore</h3>
      <p className="text-sm text-slate-500 mb-6">
        Export your complete company data as a JSON file, or restore from a previously downloaded backup.
      </p>

      {message && (
        <div className={`mb-6 p-4 rounded-lg flex items-start gap-3 text-sm ${
          messageType === 'error' ? 'bg-red-50 text-red-700 border border-red-200' :
          messageType === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
          'bg-blue-50 text-blue-700 border border-blue-200'
        }`}>
          {messageType === 'error' ? <AlertCircle size={18} className="mt-0.5 flex-shrink-0" /> :
           messageType === 'success' ? <CheckCircle2 size={18} className="mt-0.5 flex-shrink-0" /> :
           <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />}
          <div>{message}</div>
        </div>
      )}

      <div className="grid sm:grid-cols-2 gap-6">
        <div className="border border-slate-200 rounded-xl p-5 bg-slate-50">
          <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
            <Download size={18} className="text-navy-600" />
            Export Data
          </h4>
          <p className="text-xs text-slate-500 mb-4 h-12">
            Download a full copy of your company data, including accounts, invoices, contacts, and settings.
          </p>
          <button
            onClick={handleExport}
            disabled={exporting || importing}
            className="w-full flex items-center justify-center gap-2 bg-white border border-slate-300 text-slate-700 text-sm font-medium px-4 py-2 rounded-lg hover:bg-slate-50 disabled:opacity-50"
          >
            {exporting ? 'Exporting...' : 'Export Backup'}
          </button>
        </div>

        <div className="border border-slate-200 rounded-xl p-5 bg-slate-50">
          <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
            <Upload size={18} className="text-navy-600" />
            Restore Data
          </h4>
          <p className="text-xs text-slate-500 mb-4 h-12">
            Upload a previously exported backup file to restore your data. This will overwrite existing records.
          </p>
          <div className="relative">
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              disabled={exporting || importing}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
            />
            <div className={`w-full flex items-center justify-center gap-2 border border-slate-300 text-slate-700 text-sm font-medium px-4 py-2 rounded-lg ${exporting || importing ? 'bg-slate-100 opacity-50' : 'bg-white hover:bg-slate-50'}`}>
              {importing ? 'Restoring...' : 'Select Backup File'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
