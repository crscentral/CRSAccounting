# Progress Tracker — Session: Ledger sync, Financial Reports/Performance upgrades, Multi-tenant signup

Update this file as each task completes. If a new Claude session picks this up, read
ONLY this file (not the full chat history) to know exactly what's done and what's next.

## Task list

- [x] 1. Account Ledger: add Period selector to top of page (matching other pages)
      DONE: added periodProps={cp.periodProps} to PageHeader. The underlying data-fetch
      (loadEntries) already depended on cp.range.from/to, so this was purely exposing
      the existing control — no new data logic needed.
- [x] 2. Ledger sync bug: deleting a Sales/Purchase invoice must cascade-delete its ledger_entries (DB trigger fix)
      DONE: migration 18 applied live. Added BEFORE DELETE triggers on sales_invoices/purchase_invoices
      that delete matching ledger_entries. ALSO fixed a second related bug found while doing this:
      editing an invoice never re-posted its ledger entries (stale amounts stayed in ledger after edit) —
      added AFTER UPDATE triggers that delete+repost. Tested live: create test invoice -> 2 ledger entries
      posted -> delete invoice -> 0 ledger entries remain. Confirmed working.
- [x] 3. Financial Reports: add Period selector to top of page, filter balances by that period
      DONE: full rewrite of Reports.jsx. Added periodProps to PageHeader. IMPORTANT DESIGN
      DECISION: Balance Sheet accounts (Assets/Liabilities/Equity) always show cumulative
      as-of-today balances regardless of period selected (that's what a balance sheet IS -
      a snapshot, not a period total) — only Income Statement and Trial Balance actually
      filter by the selected period. Added an explanatory blue banner on-page so this isn't
      confusing. Also fixed a real bug found in the existing file: the Download Report modal
      JSX had been accidentally placed inside the wrong component (Row instead of Reports) in
      an earlier session, referencing reportModalOpen out of scope — this would have caused
      a runtime crash on page load despite the build succeeding. Fixed as part of this rewrite.
- [x] 4. Financial Performance: add Revenue & Expense breakdown-by-account section alongside existing P&L
      DONE: the "Revenue" and "Expenses" tabs (previously just a placeholder sentence) now show a real
      account-by-account table (Code/Account/Amount/% of Total) sourced from ledger_entries joined to
      accounts, filtered by the page's selected period.
- [x] 5. Financial Performance Forecast: add Projected Profit + Profit Margin % columns with clear headers
      DONE: added explicit column headers row (Month/Forecast Revenue/Forecast Expenses/Projected
      Profit/Profit Margin %) above the forecast entry grid — previously had no headers at all. Profit
      was already computed; added Profit Margin % as a new computed column.
- [x] 6. Financial Performance Forecast: add Download Report (PDF/Excel/Word) for forecast data
      DONE: added a small "Download" button next to the forecast year selector, opening a
      ReportOptionsModal with: Years to Include (Selected Year Only / Next 5 Years), Columns to
      Include (checkboxes for all 4 forecast columns), Currency.
      ALSO FIXED WHILE HERE: found and fixed the SAME misplaced-modal bug as Reports.jsx existed in
      this file too (modal was nested inside ForecastRow instead of the main component -- would have
      crashed the page at runtime). Full file rewritten cleanly, audited all other pages for the same
      pattern (Dashboard/ChartOfAccounts/Contacts/SalesInvoices/PurchaseInvoices/Analytics all confirmed OK).
- [x] 7. Multi-tenant self-service: fix "No company access yet" screen so ANY new signup can create
      their own company (not just request an invite) — makes the app sellable to separate clients
      who get their own isolated Owner access, invite their own team, with zero visibility into
      other tenants' companies. NOTE: true "admin creates password for someone else" isn't safely
      buildable client-side (needs Supabase service-role key) — self-signup + create-own-company
      is the correct/secure pattern instead. Will explain this tradeoff to user.
      DONE: built new src/components/CreateFirstCompanyScreen.jsx — replaces the old dead-end
      "ask to be invited" message in App.jsx's Gate component. Anyone with zero company
      memberships now sees a proper onboarding screen with a "Create My Company" form
      (name/currency/fiscal year), using the already-safe create_company_with_owner RPC
      (tested and confirmed safe in an earlier session — cannot be used to join/hijack an
      existing company). Also added an explainer note in Settings → Invite a User clarifying
      the distinction: "invite" = add someone to YOUR company; "share the site link" = they
      get their own fully separate company. DECISION MADE: did not build an admin-provisions-
      password-for-someone-else feature (would require a Supabase Edge Function with the
      service-role key — a materially separate, security-sensitive undertaking). Self-signup
      achieves the same end business goal (sell/give access to separate isolated clients) more
      securely (each person sets/owns their own password). Flagged this tradeoff to user; can
      build the Edge Function version later if they still want it after reading the explanation.

## ALL TASKS FROM THIS SESSION COMPLETE. Final build verified clean. Ready to package + deploy.

## Notes / decisions made
- (fill in as we go)

## Files touched this session
- (fill in as we go)
