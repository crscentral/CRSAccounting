# Guest Invoice & Daily Revenue Integration Plan

You requested that Guest Invoices automatically roll up into the Daily Revenue Collection, while still allowing manual entries for users who don't want to create individual invoices for every guest.

## Proposed Architecture: "Additive Revenue"

We will make Guest Invoices and Manual Daily Revenue work together additively. 

1. **Guest Invoice Enhancements:**
   - I will upgrade the Guest Invoice modal to allow you to input:
     - **Room Rate** and **Nights** (which will auto-calculate the Invoice Room Revenue)
     - **Other Revenue Heads** (You can add multiple line items like Spa, Breakfast, etc. to the invoice)
     - The Total Invoice Amount will be automatically calculated from these line items.

2. **Daily Revenue Collection Integration:**
   - I will update the **Daily Revenue Collection** page to automatically fetch all Guest Invoices for each day.
   - For **Room Revenue**, the table will now display:
     - `Invoiced Rooms` & `Invoiced Room Revenue` (Auto-calculated from Guest Invoices for that date)
     - `Manual Rooms` & `Manual Room Revenue` (Walk-ins or guests who didn't get an invoice, entered by you)
     - `Total Rooms` & `Total Room Revenue` (The sum of both, which will be posted to the Ledger).
   - For **Other Revenue (Ancillary)**, the table will display two sections:
     - `Invoiced Ancillary Revenue` (Auto-pulled from Guest Invoices)
     - `Manual Ancillary Revenue` (Your existing manual entries)

## User Review Required
Does this Additive Architecture sound good to you? 
If you generate a $200 invoice on Sept 16, and manually enter $1000 in Daily Revenue on Sept 16, the system will calculate your total revenue for Sept 16 as $1200. This perfectly supports hotels that have a mix of invoiced corporate clients and un-invoiced walk-in guests.
