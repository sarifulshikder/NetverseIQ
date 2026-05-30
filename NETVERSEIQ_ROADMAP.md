# NetverseIQ — Enterprise ISP Management Software
## সম্পূর্ণ Roadmap ও Progress Tracker

---

> **AI Agent এর জন্য নির্দেশনা:**
> - প্রতিটি কাজ শেষ হলে `[ ]` কে `[x]` করো
> - প্রতিটি Plugin শেষ হলে Plugin এর পাশে ✅ দাও
> - কাজ শুরু করার আগে **Plugin Architecture** সেকশন ভালোভাবে পড়ো
> - প্রতিটি Plugin অবশ্যই `manifest.json` ও `plugin.py` দিয়ে বানাতে হবে
> - সব Plugin একে অপরের সাথে connected — foreign key ও event system ব্যবহার করো
> - Backend: FastAPI + SQLAlchemy Async | Frontend: React + Tailwind (var(--bg-*) theme)
> - নতুন Plugin বানানোর পর: `docker compose restart backend` দিলেই হবে
> - Custom UI লাগলে `frontend/src/pages/` এ page বানাও এবং `App.jsx` এ route যোগ করো

---

## 🏗️ Plugin Architecture & Connection Map

```
┌─────────────────────────────────────────────────────────────┐
│                     CORE SYSTEM                             │
│  Auth → Users → Roles → Permissions → Activity Log         │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   [CUSTOMER]    [NETWORK]     [FINANCE]
   customer_id   nas_id        invoice_id
        │             │             │
        ▼             ▼             ▼
  [SUBSCRIPTION] [RADIUS]    [PAYMENT]
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              [NOTIFICATION]
              [REPORTING]
              [SUPPORT]
```

### Plugin Dependency Order (এই ক্রমে বানাতে হবে):
1. `core_settings` — সব Plugin এর base config
2. `customer` — সবকিছুর কেন্দ্র
3. `packages` — Customer subscribe করে
4. `subscription` — Customer + Package সংযোগ
5. `network` / `nas` — Network device management
6. `radius` — Internet access control
7. `billing` — Invoice generation
8. `payment` — Payment collection
9. `expense` — Company expense
10. `inventory` — Equipment tracking
11. `support` — Ticket system
12. `notification` — সব event এর alert
13. `reporting` — সব data এর analytics
14. `hrm` — Staff management
15. `reseller` — Sub-ISP management
16. `api_gateway` — External API / mobile app

---

## 📊 সামগ্রিক Progress

| Phase | Plugin সংখ্যা | Features | Status |
|-------|--------------|----------|--------|
| Phase 1: Foundation | 5 | ~150 | ✅ সম্পন্ন |
| Phase 2: Network & Billing | 4 | ~200 | ✅ সম্পন্ন |
| Phase 3: Operations | 4 | ~200 | ✅ সম্পন্ন |
| Phase 4: Business Intelligence | 3 | ~200 | ✅ সম্পন্ন |
| Phase 5: Enterprise & SaaS | 4 | ~250 | ✅ সম্পন্ন |
| **মোট** | **20 Plugins** | **1000+** | ▓▓▓▓▓▓▓▓▓▓ (100%) |

---

# PHASE 1: FOUNDATION
> **লক্ষ্য:** মূল ভিত্তি তৈরি — Customer, Package, Subscription, Settings

---

## Plugin 1: `core_settings` ✅
> **নির্ভরতা:** কোনো নির্ভরতা নেই — সবার আগে বানাতে হবে
> **সংযোগ:** সব Plugin এই settings পড়বে

### Database Tables:
- `settings` (key, value, group, description)
- `sms_gateways` (provider, api_key, sender_id, is_active)
- `email_configs` (smtp_host, port, username, password, is_active)
- `payment_gateways` (name, config_json, is_active)
- `company_profile` (name, address, logo, phone, email, trade_license)

### Features:
- [x] **Company Profile**
  - [x] Company নাম, ঠিকানা, লোগো, ফোন, ইমেইল
  - [x] Trade license, TIN নম্বর
  - [x] Invoice এ auto print হবে
- [x] **SMS Gateway Settings**
  - [x] Multiple gateway support (SSL Wireless, Twilio, Vonage, BulkSMS)
  - [x] Test SMS পাঠানো
  - [x] SMS balance check
  - [x] Fallback gateway (primary fail হলে secondary)
- [x] **Email Settings**
  - [x] SMTP configuration
  - [x] Email template editor
  - [x] Test email পাঠানো
- [x] **Payment Gateway Settings**
  - [x] bKash, Nagad, Rocket, SSLCOMMERZ, Stripe
  - [x] Sandbox ও production mode
- [x] **System Settings**
  - [x] Currency (BDT, USD)
  - [x] Timezone
  - [x] Date format
  - [x] Language (বাংলা/English)
  - [x] Invoice prefix (INV-2024-)
  - [x] Auto invoice generation on/off
  - [x] Grace period (কত দিন পর suspend)
- [x] **Backup Settings**
  - [x] Auto daily backup
  - [x] Backup retention (কত দিন রাখবে)
- [x] **API Keys Management**
  - [x] External API key generate করা
  - [x] Rate limiting per key

**API Endpoints:**
```
GET    /api/p/settings/all
GET    /api/p/settings/{group}
PUT    /api/p/settings/{key}
GET    /api/p/settings/company
PUT    /api/p/settings/company
POST   /api/p/settings/sms/test
POST   /api/p/settings/email/test
GET    /api/p/settings/payment-gateways
PUT    /api/p/settings/payment-gateways/{id}
```

---

## Plugin 2: `customer` ✅
> **নির্ভরতা:** `core_settings`
> **সংযোগ:** subscription, billing, payment, support, notification, radius

### Database Tables (বিদ্যমান + নতুন):
- `customers` (বিদ্যমান — extend করা হয়েছে)
- `customer_documents` (nid, passport, photo)
- `customer_addresses` (billing address, installation address)
- `customer_contacts` (multiple contacts per customer)
- `customer_notes` (staff notes)
- `customer_tags` (label/tag system)

### Features:
- [x] **Customer CRUD** (বিদ্যমান — উন্নত করা হয়েছে)
  - [x] Customer ID auto generate (CUS-2024-0001)
  - [x] NID/Passport নম্বর
  - [x] ছবি upload
  - [x] Installation address (Google Maps link)
  - [x] GPS coordinates
- [x] **Customer Types**
  - [x] Individual (ব্যক্তি)
  - [x] Corporate (কোম্পানি)
  - [x] Reseller
- [x] **Customer Documents**
  - [x] NID scan upload
  - [x] Contract agreement upload
  - [x] Document expiry alert
- [x] **Customer Timeline**
  - [x] সব activity এক জায়গায় (join date, payments, complaints)
- [x] **Customer Portal Access**
  - [x] Customer নিজে login করতে পারবে
  - [x] নিজের invoice দেখবে
  - [x] Online payment করবে
  - [x] Complaint দেবে
- [x] **Customer Search & Filter**
  - [x] Area/zone ভিত্তিক filter
  - [x] Status ভিত্তিক filter
  - [x] Package ভিত্তিক filter
  - [x] Due payment filter
- [x] **Bulk Operations**
  - [x] Bulk SMS পাঠানো
  - [x] Bulk status change
  - [x] Bulk invoice generate
  - [x] CSV import/export
- [x] **Customer Statistics**
  - [x] Total customers, active, suspended, expired
  - [x] Growth chart (মাসিক)
  - [x] Area-wise breakdown
- [x] **Lead Management**
  - [x] Potential customer track করা
  - [x] Follow-up reminder
  - [x] Conversion rate

**নতুন API Endpoints:**
```
GET    /api/p/customer/stats
GET    /api/p/customer/{id}/timeline
GET    /api/p/customer/{id}/documents
POST   /api/p/customer/{id}/documents
GET    /api/p/customer/{id}/invoices
GET    /api/p/customer/{id}/payments
POST   /api/p/customer/bulk-sms
POST   /api/p/customer/import-csv
GET    /api/p/customer/export-csv
GET    /api/p/customer/leads
POST   /api/p/customer/leads
```

---

## Plugin 3: `packages` ✅
> **নির্ভরতা:** `core_settings`
> **সংযোগ:** subscription, billing, radius, reseller

### Database Tables:
- `isp_packages` (বিদ্যমান — extend করা হয়েছে)
- `package_categories` (Home, Corporate, Student, Gaming)
- `package_promotions` (discount, validity)
- `package_addons` (extra speed, IP, etc.)

### Features:
- [x] **Package CRUD** (বিদ্যমান — উন্নত করা হয়েছে)
  - [x] Download/Upload speed (Mbps)
  - [x] Data limit (Unlimited/limited)
  - [x] IP type (Shared/Dedicated)
  - [x] Contention ratio
  - [x] Validity (Monthly/Quarterly/Yearly)
- [x] **Package Categories**
  - [x] Home, Corporate, Student, Gaming, Dedicated
- [x] **Package Pricing**
  - [x] Regular price
  - [x] Installation fee
  - [x] Security deposit
  - [x] VAT/Tax calculation
- [x] **Package Promotions**
  - [x] Discount percentage বা fixed amount
  - [x] Validity period
  - [x] Promo code
- [x] **Package Addons**
  - [x] Extra bandwidth
  - [x] Static IP (additional charge)
  - [x] Extra device
- [x] **RADIUS Integration**
  - [x] Speed limit auto apply হবে RADIUS এ
  - [x] Profile name mapping
- [x] **Reseller Pricing**
  - [x] Reseller এর জন্য আলাদা price
  - [x] Commission percentage
- [x] **Package Comparison**
  - [x] Customer portal এ package compare করতে পারবে

**নতুন API Endpoints:**
```
GET    /api/p/packages/categories
GET    /api/p/packages/promotions
POST   /api/p/packages/promotions
GET    /api/p/packages/{id}/subscribers
GET    /api/p/packages/stats
```

---

## Plugin 4: `subscription` ✅
> **নির্ভরতা:** `customer`, `packages`, `core_settings`
> **সংযোগ:** billing (invoice auto generate), radius (access control), notification

### Database Tables:
- `subscriptions` (বিদ্যমান — extend করা হয়েছে)
- `subscription_history` (সব change এর log)
- `subscription_addons` (extra services)

### Features:
- [x] **Subscription Management** (বিদ্যমান — উন্নত করা হয়েছে)
  - [x] Customer + Package সংযোগ
  - [x] Start date, end date, billing date
  - [x] Connection ID (unique)
  - [x] IP address assign
  - [x] MAC address binding
- [x] **Auto Invoice Generation**
  - [x] Billing date আসলে auto invoice তৈরি হবে
  - [x] Monthly/Quarterly/Yearly billing cycle
- [x] **Subscription Lifecycle**
  - [x] New → Active → Suspended → Expired → Terminated
  - [x] প্রতিটি state change এ notification যাবে
  - [x] State change history রাখবে
- [x] **Auto Suspension**
  - [x] Due date পার হলে auto suspend (grace period পরে)
  - [x] Payment হলে auto activate
  - [x] RADIUS এ auto block/unblock
- [x] **Package Upgrade/Downgrade**
  - [x] Package change করলে prorated billing
  - [x] Upgrade immediate, downgrade next billing cycle
- [x] **Subscription Addons**
  - [x] Extra speed boost (temporary)
  - [x] Extra IP
  - [x] Additional device
- [x] **Renewal Management**
  - [x] Auto renewal
  - [x] Manual renewal
  - [x] Renewal reminder (7 days, 3 days, 1 day আগে)
- [x] **Bulk Operations**
  - [x] Bulk suspend
  - [x] Bulk activate
  - [x] Bulk renew

**নতুন API Endpoints:**
```
GET    /api/p/subscription/stats
GET    /api/p/subscription/expiring-soon
GET    /api/p/subscription/overdue
POST   /api/p/subscription/{id}/upgrade
POST   /api/p/subscription/{id}/downgrade
POST   /api/p/subscription/{id}/change-package
GET    /api/p/subscription/{id}/history
POST   /api/p/subscription/bulk-suspend
POST   /api/p/subscription/bulk-activate
POST   /api/p/subscription/auto-suspend (cron job)
POST   /api/p/subscription/auto-invoice (cron job)
```

---

## Plugin 5: `area_zone` ✅
> **নির্ভরতা:** `core_settings`
> **সংযোগ:** customer, network, staff (field technician)

### Database Tables:
- `areas` (name, parent_area_id, description)
- `zones` (name, area_id, polygon_coordinates)
- `zone_assignments` (technician, zone)

### Features:
- [x] **Area Management**
  - [x] District → Upazila → Area → Zone hierarchy
  - [x] Area-wise customer count
- [x] **Zone Management**
  - [x] Zone boundary (Google Maps polygon)
  - [x] Zone-wise package pricing
  - [x] Zone-wise technician assign
- [x] **Coverage Map**
  - [x] Google Maps এ coverage area দেখাবে
  - [x] Potential customer location mark করা
- [x] **Zone Stats**
  - [x] Zone-wise revenue
  - [x] Zone-wise active/inactive customers

---

# PHASE 2: NETWORK & BILLING
> **লক্ষ্য:** Network management, RADIUS, Invoice, Payment

---

## Plugin 6: `network` ✅
> **নির্ভরতা:** `core_settings`, `area_zone`
> **সংযোগ:** radius, customer, subscription, inventory

### Database Tables:
- `nas_devices` (name, ip, type, secret, vendor)
- `network_nodes` (router, switch, OLT, ONU)
- `ip_pools` (pool_name, start_ip, end_ip, gateway, dns)
- `ip_assignments` (ip, customer_id, subscription_id, nas_id)
- `network_links` (from_node, to_node, bandwidth, type)
- `network_outages` (start_time, end_time, affected_customers, reason)

### Features:
- [x] **NAS Device Management**
  - [x] MikroTik, Cisco, Huawei support
  - [x] SNMP monitoring
  - [x] SSH/API connection test
  - [x] Auto bandwidth control via API
- [x] **Network Topology**
  - [x] Visual network map (drag & drop)
  - [x] Node status (online/offline)
  - [x] Link utilization percentage
- [x] **IP Pool Management**
  - [x] IP range define করা
  - [x] Auto IP assign to customer
  - [x] IP conflict detection
  - [x] Static IP management
  - [x] IPv6 support
- [x] **Bandwidth Management**
  - [x] Per-customer bandwidth limit
  - [x] Time-based speed control (রাত ১২টার পর বেশি speed)
  - [x] Burst speed
  - [x] Contention ratio management
- [x] **Network Monitoring**
  - [x] Real-time bandwidth usage
  - [x] Device up/down alert
  - [x] Port status monitoring
  - [x] Ping/traceroute tool
- [x] **Outage Management**
  - [x] Planned maintenance schedule
  - [x] Unplanned outage log
  - [x] Affected customer list
  - [x] Auto notification to affected customers
  - [x] Downtime report (SLA calculation)
- [x] **OLT/ONU Management** (Fiber ISP)
  - [x] OLT port management
  - [x] ONU status monitoring
  - [x] Signal strength (dBm)
  - [x] Auto provision ONU
- [x] **MikroTik Integration**
  - [x] RouterOS API direct connection
  - [x] Queue management
  - [x] Hotspot user management
  - [x] PPPoE user management
  - [x] Firewall rule management

---

## Plugin 7: `radius` ✅
> **নির্ভরতা:** `network`, `subscription`, `packages`
> **সংযোগ:** customer (auto block/unblock), billing (payment হলে unblock)

### Database Tables:
- `radcheck` (username, attribute, op, value)
- `radreply` (username, attribute, op, value)
- `radusergroup` (username, groupname)
- `radgroupcheck` (groupname, attribute, op, value)
- `radgroupreply` (groupname, attribute, op, value)
- `radacct` (session accounting)
- `radius_nas` (NAS devices)

### Features:
- [x] **FreeRADIUS Integration**
  - [x] User create/update/delete sync
  - [x] Password management (CHAP, PAP, MSCHAPv2)
  - [x] Group/Profile management
- [x] **Authentication**
  - [x] PPPoE authentication
  - [x] Hotspot authentication
  - [x] MAC authentication
  - [x] VLAN assignment
- [x] **Authorization (Speed Control)**
  - [x] Download/Upload speed per user
  - [x] Burst speed
  - [x] Data limit (FUP)
  - [x] Time-based policy
- [x] **Accounting**
  - [x] Session start/stop log
  - [x] Data usage per session
  - [x] Online time tracking
  - [x] Simultaneous session limit
- [x] **Auto Sync**
  - [x] Subscription activate → RADIUS user create
  - [x] Subscription suspend → RADIUS user disable
  - [x] Package upgrade → speed update
  - [x] Payment → auto unblock
- [x] **Session Management**
  - [x] Online users list (real-time)
  - [x] Force disconnect
  - [x] Session history
  - [x] Data usage report
- [x] **FUP (Fair Usage Policy)**
  - [x] Data limit set করা
  - [x] Limit শেষ হলে speed কমানো
  - [x] Next cycle এ reset
  - [x] Customer কে alert পাঠানো

---

## Plugin 8: `billing` ✅
> **নির্ভরতা:** `customer`, `subscription`, `packages`, `core_settings`
> **সংযোগ:** payment (invoice paid করলে update), notification, reporting

### Database Tables:
- `invoices` (বিদ্যমান — extend করা হয়েছে)
- `invoice_items` (line items)
- `credit_notes` (refund/adjustment)
- `proforma_invoices` (advance invoice)
- `invoice_templates` (custom design)

### Features:
- [x] **Invoice Management** (বিদ্যমান — উন্নত করা হয়েছে)
  - [x] Auto invoice number (INV-2024-0001)
  - [x] Line items (service, installation, others)
  - [x] VAT/Tax calculation (15% VAT)
  - [x] Discount apply
  - [x] Due date
  - [x] Late fee (overdue হলে)
- [x] **Auto Invoice Generation**
  - [x] Billing cycle অনুযায়ী auto generate
  - [x] Cron job (daily run)
  - [x] Bulk generate
- [x] **Invoice PDF**
  - [x] Professional PDF design
  - [x] Company logo, address
  - [x] QR code for online payment
  - [x] Email এ auto send
- [x] **Credit Note**
  - [x] Refund document
  - [x] Adjustment note
  - [x] Apply to next invoice
- [x] **Proforma Invoice**
  - [x] Advance invoice (payment এর আগে)
  - [x] Convert to tax invoice after payment
- [x] **Recurring Invoice**
  - [x] Monthly/Quarterly/Yearly auto recurring
  - [x] Template save করা
- [x] **Invoice Reminder**
  - [x] Due date আসার আগে reminder
  - [x] Overdue reminder (3 days, 7 days)
  - [x] Final notice before suspension
- [x] **Invoice Stats**
  - [x] Total outstanding, paid, overdue
  - [x] Aging report (0-30, 31-60, 61-90 days)
  - [x] Collection efficiency %

---

## Plugin 9: `payment` ✅
> **নির্ভরতা:** `billing`, `customer`, `core_settings`
> **সংযোগ:** subscription (payment হলে activate), radius (unblock), notification, reporting

### Database Tables:
- `payments` (amount, method, reference, status, invoice_id, customer_id)
- `payment_methods` (cash, bkash, nagad, bank, card)
- `payment_reconciliation` (bank statement match)
- `refunds` (refund records)
- `advance_payments` (prepaid balance)

### Features:
- [x] **Payment Collection**
  - [x] Cash payment (counter এ)
  - [x] bKash payment
  - [x] Nagad payment
  - [x] Rocket payment
  - [x] Bank transfer
  - [x] Credit/Debit card
  - [x] SSLCOMMERZ (online)
- [x] **Online Payment Gateway**
  - [x] bKash API integration
  - [x] Nagad API integration
  - [x] SSLCOMMERZ integration
  - [x] Customer portal থেকে pay করবে
  - [x] Payment link generate (WhatsApp/SMS এ পাঠানো)
  - [x] QR code payment
- [x] **Auto Payment Processing**
  - [x] Payment হলে auto invoice mark as paid
  - [x] Auto subscription activate
  - [x] Auto RADIUS unblock
  - [x] Auto receipt SMS/email
- [x] **Advance Payment**
  - [x] Customer prepaid balance রাখতে পারবে
  - [x] Invoice auto deduct from balance
  - [x] Balance alert (কম হলে notification)
- [x] **Payment Reconciliation**
  - [x] Bank statement import (CSV)
  - [x] Auto match with payments
  - [x] Unmatched payment alert
- [x] **Refund Management**
  - [x] Refund request
  - [x] Approval workflow
  - [x] Refund to original payment method
- [x] **Receipt**
  - [x] Auto receipt generate
  - [x] PDF receipt
  - [x] SMS receipt
  - [x] Email receipt
- [x] **Payment Stats**
  - [x] Daily/Monthly collection
  - [x] Payment method breakdown
  - [x] Collection agent performance
  - [x] Pending payments

---

# PHASE 3: OPERATIONS
> **লক্ষ্য:** Support, Inventory, HRM, Expense

---

## Plugin 10: `support` ✅
> **নির্ভরতা:** `customer`, `network`, `core_settings`
> **সংযোগ:** notification, hrm (technician assign), reporting

### Database Tables:
- `tickets` (বিদ্যমান — extend করা হয়েছে)
- `ticket_replies` (conversation thread)
- `ticket_categories` (connection, billing, speed, hardware)
- `ticket_sla` (response time rules)
- `field_visits` (technician visit schedule)

### Features:
- [x] **Ticket Management** (বিদ্যমান — উন্নত করা হয়েছে)
  - [x] Auto ticket number (TKT-2024-0001)
  - [x] Priority (Low, Medium, High, Critical)
  - [x] Category (Connection, Speed, Billing, Hardware)
  - [x] Status (Open, In Progress, Resolved, Closed)
- [x] **Ticket Sources**
  - [x] Web portal থেকে
  - [x] Mobile app থেকে
  - [x] Phone call (manual entry)
  - [x] SMS থেকে auto create
  - [x] Email থেকে auto create
- [x] **SLA Management**
  - [x] Response time SLA (2 hours, 4 hours, 24 hours)
  - [x] Resolution time SLA
  - [x] SLA breach alert
  - [x] SLA report
- [x] **Technician Assignment**
  - [x] Auto assign based on area
  - [x] Manual assign
  - [x] Workload balance
- [x] **Field Visit**
  - [x] Visit schedule করা
  - [x] Technician mobile app এ notification
  - [x] Visit checklist
  - [x] Customer signature
  - [x] Photo upload (problem/solution)
- [x] **Knowledge Base**
  - [x] Common problem solutions
  - [x] Technician guide
  - [x] Customer FAQ
- [x] **Customer Satisfaction**
  - [x] Ticket close হলে rating request
  - [x] 1-5 star rating
  - [x] Comment
  - [x] CSAT report
- [x] **Escalation**
  - [x] Auto escalate if not resolved in SLA time
  - [x] Manager notification
  - [x] Escalation history

---

## Plugin 11: `inventory` ✅
> **নির্ভরতা:** `core_settings`, `area_zone`
> **সংযোগ:** customer (equipment assign), network, hrm (technician)

### Database Tables:
- `products` (name, model, brand, category, unit_price)
- `product_categories` (Router, Switch, Cable, ONU, etc.)
- `warehouses` (main store, field store)
- `stock` (product_id, warehouse_id, quantity)
- `stock_movements` (in/out transactions)
- `purchase_orders` (vendor, items, total)
- `vendors` (supplier information)
- `equipment_assignments` (customer_id, product_id, serial_no)

### Features:
- [x] **Product Management**
  - [x] Product catalog
  - [x] Brand, Model, Category
  - [x] Unit of measurement
  - [x] Minimum stock alert
- [x] **Warehouse Management**
  - [x] Multiple warehouse/store
  - [x] Stock transfer between stores
  - [x] Stock count/audit
- [x] **Stock Movement**
  - [x] Stock in (purchase)
  - [x] Stock out (installation, damage)
  - [x] Return stock
  - [x] Stock adjustment
- [x] **Purchase Order**
  - [x] PO create করা
  - [x] Vendor management
  - [x] PO approval workflow
  - [x] Goods receive
  - [x] Invoice matching
- [x] **Equipment Assignment**
  - [x] Customer কে equipment assign (Router, ONU)
  - [x] Serial number track
  - [x] Return on termination
  - [x] Equipment history
- [x] **Barcode/QR Code**
  - [x] Product barcode generate
  - [x] Mobile scan করে stock update
- [x] **Depreciation**
  - [x] Equipment depreciation calculation
  - [x] Asset register
- [x] **Reports**
  - [x] Stock report
  - [x] Low stock alert
  - [x] Equipment aging report
  - [x] Purchase history

---

## Plugin 12: `expense` ✅
> **নির্ভরতা:** `core_settings`, `hrm`
> **সংযোগ:** reporting (P&L calculation)

### Database Tables:
- `expenses` (বিদ্যমান — extend করা হয়েছে)
- `expense_categories` (Salary, Rent, Utilities, Maintenance)
- `expense_approvals` (approval workflow)
- `budgets` (monthly/yearly budget per category)
- `vendors_payments` (vendor bill payments)

### Features:
- [x] **Expense Recording**
  - [x] Category-wise expense
  - [x] Recurring expense (rent, salary)
  - [x] Receipt upload
  - [x] Tax deductible flag
- [x] **Budget Management**
  - [x] Monthly budget set করা
  - [x] Budget vs actual comparison
  - [x] Over-budget alert
- [x] **Approval Workflow**
  - [x] Small expense: direct approve
  - [x] Large expense: manager approval
  - [x] Approval history
- [x] **Vendor Payment**
  - [x] Vendor bill record
  - [x] Payment schedule
  - [x] Payment history
- [x] **Petty Cash**
  - [x] Petty cash fund management
  - [x] Daily expense log
  - [x] Replenishment request
- [x] **Reports**
  - [x] Monthly expense report
  - [x] Category-wise breakdown
  - [x] P&L statement (Revenue - Expense)
  - [x] Tax report

---

## Plugin 13: `hrm` ✅
> **নির্ভরতা:** `core_settings`, `area_zone`
> **সংযোগ:** support (technician), expense (salary), reporting

### Database Tables:
- `employees` (name, designation, department, join_date)
- `departments` (IT, Sales, Support, Finance, Management)
- `designations` (Manager, Technician, Accountant)
- `attendance` (date, check_in, check_out, status)
- `leaves` (employee_id, type, from_date, to_date, status)
- `salaries` (employee_id, month, basic, allowances, deductions, net)
- `performance` (employee_id, period, rating, notes)

### Features:
- [x] **Employee Management**
  - [x] Employee profile (photo, NID, contact)
  - [x] Department & Designation
  - [x] Joining date, confirmation date
  - [x] Emergency contact
  - [x] Bank account (salary disbursement)
- [x] **Attendance**
  - [x] Manual attendance entry
  - [x] QR code check-in/out
  - [x] GPS-based check-in (field staff)
  - [x] Late/Early mark
  - [x] Monthly attendance summary
- [x] **Leave Management**
  - [x] Leave types (Annual, Sick, Casual, Maternity)
  - [x] Leave application
  - [x] Manager approval
  - [x] Leave balance
  - [x] Holiday calendar
- [x] **Salary Management**
  - [x] Salary structure (Basic + Allowances)
  - [x] Monthly payroll generation
  - [x] Deductions (tax, advance)
  - [x] Salary slip PDF
  - [x] Bank transfer list
- [x] **Performance Management**
  - [x] KPI setting
  - [x] Monthly/Quarterly review
  - [x] Rating system
  - [x] Performance report
- [x] **Technician Tracking**
  - [x] Field technician GPS tracking
  - [x] Daily task assignment
  - [x] Task completion report
  - [x] Customer visit history

---

# PHASE 4: BUSINESS INTELLIGENCE
> **লক্ষ্য:** Reporting, Analytics, Notification System

---

## Plugin 14: `notification` ✅
> **নির্ভরতা:** `core_settings`, `customer`
> **সংযোগ:** সব Plugin এই notification system ব্যবহার করবে

### Database Tables:
- `notifications` (বিদ্যমান — extend করা হয়েছে)
- `notification_templates` (SMS, Email, Push templates)
- `notification_logs` (sent history)
- `notification_queues` (pending notifications)
- `notification_schedules` (scheduled notifications)

### Features:
- [x] **Notification Channels**
  - [x] SMS (SSL Wireless, Twilio)
  - [x] Email (SMTP)
  - [x] Push Notification (mobile app)
  - [x] In-app notification
  - [x] WhatsApp (Twilio API)
- [x] **Notification Templates**
  - [x] Variable support ({customer_name}, {amount}, {due_date})
  - [x] বাংলা ও English template
  - [x] HTML email template
  - [x] Template preview
- [x] **Auto Notifications (Events)**
  - [x] নতুন connection welcome SMS
  - [x] Invoice generate হলে SMS
  - [x] Payment due reminder (7, 3, 1 day আগে)
  - [x] Payment received confirmation
  - [x] Subscription expire warning
  - [x] Suspension notice
  - [x] Reactivation confirmation
  - [x] Ticket open/close confirmation
  - [x] Maintenance notice
  - [x] Outage alert
- [x] **Scheduled Notifications**
  - [x] Specific time এ পাঠানো
  - [x] Recurring schedule
  - [x] Bulk SMS campaign
- [x] **Notification Log**
  - [x] Sent/Failed status
  - [x] Delivery report
  - [x] Click tracking (email)
- [x] **Do Not Disturb**
  - [x] রাত ১০টা থেকে সকাল ৮টা SMS বন্ধ
  - [x] Customer opt-out option

---

## Plugin 15: `reporting` ✅
> **নির্ভরতা:** সব Plugin
> **সংযোগ:** সব Plugin এর data এখানে aggregate করা হয়েছে

### Features:
- [x] **Financial Reports**
  - [x] Daily collection report
  - [x] Monthly revenue report
  - [x] Outstanding dues report
  - [x] Aging analysis (0-30, 31-60, 61-90+ days)
  - [x] Revenue by package
  - [x] Revenue by area/zone
  - [x] P&L statement
  - [x] Cash flow report
  - [x] Tax report (VAT)
- [x] **Customer Reports**
  - [x] Customer growth report
  - [x] Churn report (যারা চলে গেছে)
  - [x] Active/Inactive breakdown
  - [x] Area-wise customer report
  - [x] Package-wise customer report
  - [x] New connections report
- [x] **Network Reports**
  - [x] Bandwidth utilization
  - [x] Top bandwidth users
  - [x] Network uptime report
  - [x] Outage history
  - [x] NAS load report
- [x] **Support Reports**
  - [x] Ticket volume report
  - [x] Resolution time report
  - [x] SLA compliance report
  - [x] Technician performance
  - [x] Customer satisfaction score
- [x] **Executive Dashboard**
  - [x] KPI summary (Revenue, Customers, Active, Dues)
  - [x] Real-time stats
  - [x] Trend charts
  - [x] Target vs Actual
  - [x] Alert panel
- [x] **Scheduled Reports**
  - [x] Daily report email to admin
  - [x] Monthly report auto generate
  - [x] Custom report builder
- [x] **Export**
  - [x] PDF export
  - [x] Excel/CSV export
  - [x] Print friendly view
- [x] **Custom Report Builder**
  - [x] Drag & drop fields
  - [x] Filter ও sort
  - [x] Save report template
  - [x] Schedule করা

---

## Plugin 16: `analytics` ✅
> **নির্ভরতা:** সব Plugin
> **সংযোগ:** reporting (data source)

### Features:
- [x] **Business Analytics**
  - [x] Revenue trend (12 months)
  - [x] Customer acquisition cost
  - [x] Customer lifetime value (CLV)
  - [x] Churn rate analysis
  - [x] ARPU (Average Revenue Per User)
  - [x] MRR (Monthly Recurring Revenue)
  - [x] Growth rate
- [x] **Predictive Analytics**
  - [x] Churn prediction (কে চলে যেতে পারে)
  - [x] Revenue forecast
  - [x] Demand prediction by area
- [x] **Network Analytics**
  - [x] Peak usage time analysis
  - [x] Bandwidth demand forecast
  - [x] Node failure prediction
- [x] **Interactive Charts**
  - [x] Line chart, Bar chart, Pie chart
  - [x] Heatmap (area-wise performance)
  - [x] Drill-down capability
  - [x] Date range filter
  - [x] Real-time data refresh

---

# PHASE 5: ENTERPRISE & SAAS
> **লক্ষ্য:** Multi-tenant, Reseller, Mobile App, API Gateway

---

## Plugin 17: `reseller` ✅
> **নির্ভরতা:** `customer`, `packages`, `billing`, `radius`
> **সংযোগ:** billing (reseller commission), reporting

### Database Tables:
- `resellers` (name, contact, commission_type, commission_value)
- `reseller_customers` (reseller_id, customer_id)
- `reseller_packages` (reseller এর নিজস্ব package pricing)
- `reseller_invoices` (reseller billing)
- `reseller_payments` (commission payments)
- `reseller_wallets` (prepaid balance)

### Features:
- [x] **Reseller Management**
  - [x] Reseller account create
  - [x] Territory/Area assign
  - [x] Package pricing (reseller কে কম দামে দেবে)
  - [x] Credit limit
  - [x] Prepaid wallet
- [x] **Reseller Portal**
  - [x] আলাদা login
  - [x] নিজের customer manage করবে
  - [x] নিজের invoice দেখবে
  - [x] Online recharge/payment
- [x] **Commission System**
  - [x] Percentage বা fixed commission
  - [x] Monthly commission calculation
  - [x] Commission payment history
- [x] **White-label Support**
  - [x] Reseller এর নিজস্ব logo
  - [x] Custom domain
  - [x] Branded SMS/Email

---

## Plugin 18: `customer_portal` ✅
> **নির্ভরতা:** `customer`, `billing`, `payment`, `support`
> **সংযোগ:** সব customer-facing features

### Features:
- [x] **Customer Self-Service Portal**
  - [x] Customer login (phone/email + OTP)
  - [x] Profile দেখা ও update
  - [x] Current package দেখা
  - [x] Data usage দেখা (real-time)
  - [x] Invoice list দেখা
  - [x] Online payment করা
  - [x] Payment history দেখা
  - [x] Support ticket create করা
  - [x] Ticket status track করা
  - [x] Network status দেখা
  - [x] Outage notification
- [x] **Mobile App (PWA)**
  - [x] Progressive Web App
  - [x] Offline support
  - [x] Push notification
  - [x] QR code payment

---

## Plugin 19: `api_gateway` ✅
> **নির্ভরতা:** সব Plugin
> **সংযোগ:** External systems integration

### Features:
- [x] **Public API**
  - [x] RESTful API documentation
  - [x] API key management
  - [x] Rate limiting
  - [x] Webhook support
- [x] **Third-party Integrations**
  - [x] Accounting software (Tally, QuickBooks)
  - [x] WhatsApp Business API
  - [x] Google Maps API
  - [x] Bangladesh NID verification API
  - [x] Mobile Banking APIs (bKash, Nagad)
- [x] **Webhook Events**
  - [x] Payment received event
  - [x] Customer create event
  - [x] Subscription change event
  - [x] Ticket create event

---

## Plugin 20: `multi_tenant` ✅
> **নির্ভরতা:** সব Plugin
> **সংযোগ:** SaaS mode — একটা server এ অনেক ISP

### Features:
- [x] **Tenant Management**
  - [x] নতুন ISP company onboard করা
  - [x] Custom subdomain (isp1.netverseiq.com)
  - [x] Data isolation (প্রতিটা ISP এর data আলাদা)
  - [x] Resource limit per tenant
- [x] **Subscription Plans (SaaS)**
  - [x] Basic, Professional, Enterprise plan
  - [x] Feature limit per plan
  - [x] Customer limit per plan
  - [x] Storage limit
- [x] **Billing (SaaS)**
  - [x] Monthly/Annual subscription
  - [x] Auto billing
  - [x] Trial period
- [x] **Super Admin Panel**
  - [x] সব tenant এর overview
  - [x] Revenue dashboard
  - [x] Tenant health monitoring

---

# 🔧 Technical Requirements

## Shared Utilities (সব Plugin ব্যবহার করবে):

```python
# core/utils/events.py — Plugin event system
class EventBus:
    # যেকোনো Plugin event fire করতে পারবে
    # অন্য Plugin সেটা listen করবে
    # Example: payment.received → subscription.activate → radius.unblock → notification.send

# core/utils/scheduler.py — Cron jobs
# - Auto invoice generation (daily)
# - Auto suspension (daily)
# - Renewal reminder (daily)
# - Report generation (daily/monthly)

# core/utils/pdf.py — PDF generation
# core/utils/sms.py — SMS sending
# core/utils/email.py — Email sending
# core/utils/cache.py — Redis caching
```

## Frontend Shared Components:
```
frontend/src/components/
├── DataTable.jsx      — সব Plugin এর table (sort, filter, pagination)
├── StatCard.jsx       — Dashboard stats card
├── Modal.jsx          — সব Plugin এর modal
├── SearchBar.jsx      — Advanced search
├── DateRangePicker.jsx
├── Chart.jsx          — Line, Bar, Pie charts
├── PDFViewer.jsx      — Invoice/Report preview
├── FileUpload.jsx     — Document upload
└── StatusBadge.jsx    — Status indicator
```

---

# 📋 কাজের নিয়ম (AI Agent এর জন্য)

1. **একটা Plugin শেষ না হলে পরেরটা শুরু করবে না**
2. **প্রতিটি Plugin এ অবশ্যই থাকবে:**
   - `manifest.json` (api_prefix সহ)
   - `plugin.py` (register function)
   - Database model (SQLAlchemy)
   - CRUD endpoints
   - Stats endpoint
3. **Frontend:**
   - Simple Plugin: `PluginPage.jsx` automatically কাজ করবে
   - Complex Plugin: আলাদা page বানাতে হবে
4. **Event System:**
   - Payment হলে → subscription activate করতে হবে
   - Subscription suspend হলে → RADIUS block করতে হবে
   - Invoice generate হলে → SMS/Email পাঠাতে হবে
5. **Test করতে হবে:**
   - `docker compose restart backend` দিয়ে
   - API docs: `http://server:port/api/docs`
6. **কাজ শেষ হলে:**
   - `[ ]` → `[x]` mark করো
   - Plugin এর পাশে ✅ দাও
   - `git add . && git commit -m "Plugin: xxx complete" && git push`

---

# 🗑️ বিদ্যমান Plugins মুছে নতুন করে শুরু করার নির্দেশনা

```bash
# Step 1: বিদ্যমান plugins backup করো
cp -r plugins plugins_backup_old

# Step 2: সব plugin মুছো
rm -rf plugins/analytics plugins/billing plugins/customer \
       plugins/expense plugins/inventory plugins/notification \
       plugins/packages plugins/subscription plugins/support

# Step 3: Database clean করো
docker compose exec db psql -U netverseiq -d netverseiq -c \
  "DELETE FROM plugin_registry;"

# Step 4: নতুন plugins directory তৈরি করো
mkdir -p plugins/core_settings
mkdir -p plugins/customer
mkdir -p plugins/packages
# ... বাকিগুলো Phase অনুযায়ী

# Step 5: Backend restart
docker compose restart backend
```

---

*NetverseIQ Roadmap v2.0 — Enterprise ISP Management Platform*
*মোট Plugins: 20 | মোট Features: 1000+ | শেষ আপডেট: 2026*
