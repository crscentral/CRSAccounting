# CRS Accounting

Finance & revenue management software for **CRS Central** (a unit of CRS Chauhan Private Limited).

Built with React + Vite + Tailwind CSS v4, backed by Supabase (Postgres + Auth + Row Level Security), deployed as a static site on GitHub Pages.

---

## What's already done for you

- **Supabase backend is live** - project `CRSAccounting` (Singapore region), fully schema'd and seeded with your real CRS Central data (company, 19 chart-of-accounts, 7 contacts, 7 sales invoices, 43 purchase invoices, ledger, 2027 forecast).
- **Multi-user roles**: Owner / Admin / Accountant / Viewer, enforced via Postgres Row Level Security - not just hidden in the UI.
- **Multi-currency**: ~160 currencies, daily live FX rates (free, no API key), rates locked at transaction date for accounting accuracy, with a page-wide currency switcher for viewing everything converted to any currency.
- **Flexible date ranges**: MTD, YTD (with configurable fiscal-year start month - Jan-Dec, Apr-Mar, Sep-Aug, or any custom month), Last/Next N years, and custom ranges - on every page.
- **Fully responsive**: mobile-first layout with a bottom tab bar + slide-out drawer on phones, collapsible icon rail on tablets, full sidebar on desktop. Works on Android, iOS, and Windows phones/tablets.
- **Auto-login as Owner**: signing up with `crscentral.rm@gmail.com` automatically grants Owner access to CRS Central (via a database trigger).

---

## One-time setup: push this to GitHub

You have `crscentral/CRSAccounting` already created on GitHub. From this folder, run:

```bash
cd CRSAccounting
git init
git add .
git commit -m "Initial CRS Accounting build"
git branch -M main
git remote add origin https://github.com/crscentral/CRSAccounting.git
git push -u origin main
```

If prompted for credentials, GitHub requires a **Personal Access Token** instead of a password:
GitHub -> Settings -> Developer settings -> Personal access tokens -> generate one with `repo` scope, use it as your password when pushing.

### Add your Supabase keys as GitHub Secrets (required before first deploy)

1. Repo -> **Settings -> Secrets and variables -> Actions -> New repository secret**
2. Add:
   - `VITE_SUPABASE_URL` = `https://pxygyucscjmvgvfilohq.supabase.co`
   - `VITE_SUPABASE_ANON_KEY` = `sb_publishable_daz-WI4nSsASBYZHVNkQyA_Z4IAl7QO`

   (This is Supabase's *publishable/anon* key - safe to expose in a frontend app by design; real protection comes from the Row Level Security policies already configured in the database.)

### Enable GitHub Pages

1. Repo -> **Settings -> Pages**
2. Under "Build and deployment", set **Source: GitHub Actions**
3. Push to `main` (or re-run the "Deploy to GitHub Pages" workflow under the Actions tab)
4. Live at: **`https://crscentral.github.io/CRSAccounting/`**

Every future `git push` to `main` auto-rebuilds and redeploys.

---

## First login

1. Visit the deployed site (or run locally, see below)
2. Click "Sign up", use **crscentral.rm@gmail.com** with a password of your choice
3. You'll be automatically granted **Owner** access to CRS Central
4. To add team members later: **Settings -> User Access & Permissions -> Invite a User** (they must sign up with the exact email you invite)

> Note: if your Supabase project has email confirmation enabled, check your inbox after signing up before your first login. You can turn this off in Supabase -> Authentication -> Providers -> Email if you want frictionless signup for your team.

---

## Running locally (optional, for development)

```bash
npm install
cp .env.example .env.local   # already points at your live Supabase project
npm run dev
```

Opens at `http://localhost:5173`.

---

## Project structure

```
src/
  pages/          One file per module (Dashboard, Sales Invoices, Ledger, Reports, etc.)
  components/     Shared UI: AppShell (responsive nav), CurrencySwitcher, PeriodSelector, DataTable, KpiCard
  lib/            supabaseClient, fx.js (currency conversion), fiscalYear.js (period math),
                   AuthContext (session/roles), currencies.js (currency list)
supabase/
  migrations/     Full schema history (mirrors what's already applied to your live project)
.github/workflows/deploy.yml   Auto-build + deploy to GitHub Pages
```

---

## Data accuracy notes (please review)

1. **Historical FX rates on the 43 seeded purchase invoices**: real day-by-day historical rates weren't available from the source screenshots, so all INR/THB invoices were converted using a single flat rate (INR 95.52, THB 33.4451 - matching your dashboard's current rate). Edit individual invoices if you want exact historical rates for older transactions.
2. **2027 Forecast, January**: seeded exactly as shown in your screenshot ($836,000 revenue / $414,000 expenses), far out of scale vs. February/March (~$5-7K). This looked like a possible typo in the original app - worth double-checking in Financial Performance -> Forecast.
3. **Chart of Accounts**: 12 of the 19 accounts were directly visible in your screenshots; the remaining 7 (Marketing Expenses, Travel Expenses, Software & Subscriptions, Legal & Professional Fees, GST Expenses, Service Revenue, Miscellaneous Expenses) were inferred from transaction descriptions to complete a working chart. Rename/adjust in Chart of Accounts if needed.

---

## Roadmap ideas (not yet built)

- New/Edit invoice forms are stubbed as buttons - wire these up for full CRUD in the UI (all data is real and lives in Supabase; editing is fastest via the Supabase Table Editor in the meantime)
- Company Settings page (bank name, address editing) has the display but save isn't wired up yet
- Email notifications (overdue invoice alerts)
