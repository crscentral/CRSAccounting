import React from 'react'

export default function PrivacyPolicy() {
  return (
    <div className="p-4 md:p-8 max-w-3xl mx-auto font-body">
      <div className="mb-8">
        <h1 className="text-2xl md:text-3xl font-display font-bold text-navy-700">Privacy Policy & Non-Disclosure of Data</h1>
        <p className="text-slate-500 mt-2">Commitment to Privacy</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8 space-y-8 text-slate-600 leading-relaxed text-sm md:text-base">
        <p>
          This Privacy Policy outlines how <strong className="text-navy-700">CRS Accounting</strong> (owned and operated by CRS Central - A Unit of CRS Chauhan Private Limited) collects, protects, and handles your data. Your privacy is our top priority.
        </p>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-navy-700">1. Data Ownership</h2>
          <p>You retain 100% ownership of all financial data, contacts, and records you enter into CRS Accounting. We claim no ownership over your business data.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-navy-700">2. Strict Non-Disclosure</h2>
          <p>We operate under a strict policy of non-disclosure. We will <strong>never</strong> sell, rent, trade, or expose your financial data, customer lists, or business metrics to any third party, marketing agency, or external organization.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-navy-700">3. How We Use Your Data</h2>
          <p>The data you enter is used exclusively by our servers to provide you with the CRS Accounting software services (such as generating your ledgers, calculating your dashboards, and rendering your invoices). Our staff and developers do not monitor, review, or access your raw financial data unless you explicitly request technical support that requires us to do so.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-navy-700">4. Zero-Knowledge Password Protection</h2>
          <p>We never store your raw passwords. We use advanced cryptographic hashing to scramble your credentials, meaning nobody—not even our system administrators—can retrieve your password.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-navy-700">5. Data Deletion</h2>
          <p>You have the right to request the complete deletion of your company profile and associated data from our active servers at any time.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-navy-700">6. Legal Compliance</h2>
          <p>We will only disclose your information if strictly required to do so by a valid, legally binding subpoena or court order, and we will attempt to notify you before any such disclosure occurs.</p>
        </section>

        <div className="pt-8 border-t border-slate-100 text-center">
          <p className="text-sm text-slate-500 italic">
            CRS Accounting is proudly owned and operated by<br/>
            <strong className="text-slate-700 not-italic">CRS Central - A Unit of CRS Chauhan Private Limited.</strong>
          </p>
        </div>
      </div>
    </div>
  )
}
