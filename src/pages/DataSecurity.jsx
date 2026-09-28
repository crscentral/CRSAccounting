import React from 'react'
import { ShieldCheck, Lock, Database, Server } from 'lucide-react'

export default function DataSecurity() {
  return (
    <div className="p-4 md:p-8 max-w-4xl mx-auto font-body">
      <div className="mb-8">
        <h1 className="text-2xl md:text-3xl font-display font-bold text-navy-700">Data Safety & Security</h1>
        <p className="text-slate-500 mt-2">Your Data. Strictly Isolated. Fully Secured.</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8 space-y-8">
        <p className="text-slate-600 leading-relaxed">
          At <strong className="text-navy-700">CRS Accounting</strong> (owned and operated by CRS Central - A Unit of CRS Chauhan Private Limited), we understand that your financial data is the lifeblood of your business. We treat your data with the highest level of confidentiality and protect it using enterprise-grade security architecture.
        </p>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="flex gap-4">
            <div className="shrink-0 w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
              <Database className="text-blue-600 w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-navy-700 mb-1">Absolute Data Isolation</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                We employ strict, mathematically enforced Row Level Security (RLS) within our database infrastructure. Your financial records, invoices, and contacts are cryptographically locked exclusively to your specific company profile. It is physically impossible for another company using our software to view or access your data.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="shrink-0 w-10 h-10 rounded-full bg-green-50 flex items-center justify-center">
              <Lock className="text-green-600 w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-navy-700 mb-1">End-to-End Encryption</h3>
              <ul className="text-sm text-slate-600 leading-relaxed list-disc ml-4 space-y-1">
                <li><strong>In Transit:</strong> All communications between your device and our servers are secured using industry-standard HTTPS/TLS encryption.</li>
                <li><strong>At Rest:</strong> Your data is securely hosted on world-class cloud infrastructure. Every piece of data stored on our servers is protected by AES-256 encryption.</li>
              </ul>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="shrink-0 w-10 h-10 rounded-full bg-purple-50 flex items-center justify-center">
              <ShieldCheck className="text-purple-600 w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-navy-700 mb-1">Advanced Threat Protection</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Our platform utilizes secure, parameterized queries that completely neutralize SQL Injection attacks. Because our software operates purely as a secure web application within your browser's sandbox, it is effectively immune to traditional computer viruses and malware.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="shrink-0 w-10 h-10 rounded-full bg-orange-50 flex items-center justify-center">
              <Server className="text-orange-600 w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-navy-700 mb-1">Data Backups & Recovery</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                While we maintain master system backups for catastrophic server failures, we empower our clients to manage their own data safety. You can download a complete backup of your company's data at any time via the "Backup & Restore" tab in your Settings.
              </p>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-100 text-center">
          <p className="text-sm text-slate-500 italic">
            CRS Accounting is proudly owned and operated by<br/>
            <strong className="text-slate-700 not-italic">CRS Central - A Unit of CRS Chauhan Private Limited.</strong>
          </p>
        </div>
      </div>
    </div>
  )
}
