#!/usr/bin/env python3
"""Expanded seed script for fintechaccountant - rich demo data.

Creates:
  - 7 demo users (admin, student, CA, instructor x2, employer x2)
  - Instructor profiles, employer profiles
  - 8 course categories + 12 courses with modules and lessons
  - 12 job categories + 12 jobs
  - 10 communities (8 official)
  - 4 upcoming events
  - Skills attached to profiles

Run: python manage.py shell -c "exec(open('scripts/seed.py').read()); run()"
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, Role
from apps.profiles.models import Profile, ProfileSkill, Skill
from apps.courses.models import Category, Course, Module, Lesson
from apps.careers.models import JobCategory, Job
from apps.communities.models import Community
from apps.employers.models import EmployerProfile
from apps.instructors.models import InstructorProfile
from apps.events.models import Event


def _user(email, first, role_codes, last='', **kwargs):
    u, created = User.objects.get_or_create(
        email=email,
        defaults={'first_name': first, 'last_name': last, 'is_active': True, **kwargs},
    )
    if created:
        u.set_password('demo1234')
        u.save()
        for code in role_codes:
            u.add_role(code)
    return u


# Catalog of courses: (title, category_name, level, is_free, price, hours, subtitle, desc, [(module_title, [(lesson_title, type, mins, is_preview)])])
COURSES = [
    ('GST Practitioner - Complete Course', 'Taxation', Course.INTERMEDIATE, True, 0, 20,
     'Master GST from basics to advanced',
     'A complete course on GST including registration, returns, input credit, audits and annual returns. Practical examples and case studies included.',
     [('Module 1: GST Basics', [
        ('Introduction to GST', Lesson.VIDEO, 15, True),
        ('GST Registration Process', Lesson.VIDEO, 25, False),
        ('Composition Scheme', Lesson.VIDEO, 20, False),
        ('Quiz: GST Basics', Lesson.QUIZ, 10, False),
       ]),
      ('Module 2: GST Returns', [
        ('GSTR-1 Filing', Lesson.VIDEO, 30, False),
        ('GSTR-3B Filing', Lesson.VIDEO, 35, False),
        ('Input Tax Credit Reconciliation', Lesson.VIDEO, 40, False),
        ('Assignment: File a mock GSTR-3B', Lesson.ASSIGNMENT, 60, False),
       ]),
     ]),
    ('Income Tax Fundamentals', 'Taxation', Course.BEGINNER, True, 0, 15,
     'Understand income tax from scratch',
     'A beginner-friendly introduction to income tax, slabs, deductions and return filing for individuals.',
     [('Module 1: Basics', [
        ('What is Income Tax?', Lesson.VIDEO, 12, True),
        ('Heads of Income', Lesson.VIDEO, 22, False),
        ('Tax Slabs Explained', Lesson.VIDEO, 18, False),
       ]),
      ('Module 2: Deductions & Filing', [
        ('Section 80C Deductions', Lesson.VIDEO, 20, False),
        ('Filing ITR-1 (Sahaj)', Lesson.VIDEO, 30, False),
       ]),
     ]),
    ('Tally Prime - From Zero to Pro', 'Software', Course.BEGINNER, False, 999, 25,
     "Master India's most popular accounting software",
     'Complete hands-on training on Tally Prime covering company creation, vouchers, inventory, GST and reports.',
     [('Module 1: Getting Started', [
        ('Installation & Setup', Lesson.VIDEO, 10, True),
        ('Company Creation', Lesson.VIDEO, 15, False),
        ('Chart of Accounts', Lesson.VIDEO, 20, False),
       ]),
      ('Module 2: Vouchers & Inventory', [
        ('Accounting Vouchers', Lesson.VIDEO, 30, False),
        ('Inventory Management', Lesson.VIDEO, 25, False),
        ('GST in Tally', Lesson.VIDEO, 35, False),
       ]),
     ]),
    ('Advanced Excel for Finance', 'Software', Course.INTERMEDIATE, False, 1499, 18,
     'Excel skills every finance professional needs',
     'Master PivotTables, lookup functions, dashboards and financial modelling basics in Excel.',
     [('Module 1: Formulas & Functions', [
        ('VLOOKUP & HLOOKUP', Lesson.VIDEO, 18, True),
        ('INDEX-MATCH & XLOOKUP', Lesson.VIDEO, 22, False),
        ('IF, IFS & Nested Logic', Lesson.VIDEO, 20, False),
       ]),
      ('Module 2: Data Analysis', [
        ('PivotTables Deep Dive', Lesson.VIDEO, 30, False),
        ('Building Dashboards', Lesson.VIDEO, 35, False),
        ('Assignment: Build a Sales Dashboard', Lesson.ASSIGNMENT, 90, False),
       ]),
     ]),
    ('Financial Modelling Mastery', 'Finance', Course.ADVANCED, False, 2999, 30,
     'Build professional financial models from scratch',
     'Learn to build 3-statement models, DCF valuations and sensitivity analyses used in investment banking and FP&A.',
     [('Module 1: 3-Statement Model', [
        ('Setting up the Model', Lesson.VIDEO, 25, True),
        ('Income Statement Build', Lesson.VIDEO, 40, False),
        ('Balance Sheet & Cash Flow', Lesson.VIDEO, 45, False),
       ]),
      ('Module 2: DCF Valuation', [
        ('WACC Calculation', Lesson.VIDEO, 30, False),
        ('Terminal Value', Lesson.VIDEO, 25, False),
        ('Sensitivity Analysis', Lesson.VIDEO, 35, False),
       ]),
     ]),
    ('Financial Accounting Basics', 'Accounting', Course.BEGINNER, True, 0, 12,
     'The foundation every accountant needs',
     'Learn double-entry bookkeeping, journal entries, ledgers, trial balance and final accounts.',
     [('Module 1: Bookkeeping', [
        ('Double-Entry System', Lesson.VIDEO, 15, True),
        ('Journal Entries', Lesson.VIDEO, 20, False),
        ('Ledger & Trial Balance', Lesson.VIDEO, 25, False),
       ]),
      ('Module 2: Final Accounts', [
        ('Trading Account', Lesson.VIDEO, 20, False),
        ('Profit & Loss and Balance Sheet', Lesson.VIDEO, 30, False),
       ]),
     ]),
    ('TDS & TCS Complete Guide', 'Taxation', Course.INTERMEDIATE, False, 799, 10,
     'Everything about Tax Deducted at Source',
     'Comprehensive guide on TDS sections, rates, returns, certificates and TCS provisions under the Income Tax Act.',
     [('Module 1: TDS Basics', [
        ('What is TDS?', Lesson.VIDEO, 12, True),
        ('TDS Sections & Rates', Lesson.VIDEO, 25, False),
       ]),
      ('Module 2: Compliance', [
        ('TDS Returns (24Q/26Q)', Lesson.VIDEO, 30, False),
        ('TDS Certificates (Form 16/16A)', Lesson.VIDEO, 20, False),
       ]),
     ]),
    ('Python for Accountants', 'Technology', Course.BEGINNER, True, 0, 16,
     'Automate your accounting work with Python',
     'Learn Python basics with accounting-focused examples: automate Excel, parse bank statements, generate reports.',
     [('Module 1: Python Basics', [
        ('Variables & Data Types', Lesson.VIDEO, 15, True),
        ('Control Flow', Lesson.VIDEO, 20, False),
        ('Functions', Lesson.VIDEO, 18, False),
       ]),
      ('Module 2: Automating Accounting Tasks', [
        ('Reading Excel with openpyxl', Lesson.VIDEO, 25, False),
        ('Parsing Bank Statements', Lesson.VIDEO, 30, False),
        ('Generating PDF Reports', Lesson.VIDEO, 28, False),
       ]),
     ]),
    ('Digital Payments & FinTech', 'FinTech', Course.INTERMEDIATE, True, 0, 14,
     "Understand India's digital payment ecosystem",
     'UPI, wallets, BBPS, AEPS and the future of digital payments in India. Includes regulatory framework.',
     [('Module 1: Payment Landscape', [
        ('Evolution of Digital Payments', Lesson.VIDEO, 15, True),
        ('UPI Deep Dive', Lesson.VIDEO, 25, False),
       ]),
      ('Module 2: FinTech & Regulation', [
        ('RBI Regulations', Lesson.VIDEO, 22, False),
        ('Future of FinTech', Lesson.VIDEO, 18, False),
       ]),
     ]),
    ('Stock Market Fundamentals', 'Capital Markets', Course.BEGINNER, True, 0, 10,
     'Start your investing journey',
     'Learn how stock markets work, basic analysis, IPO process and how to start investing in Indian markets.',
     [('Module 1: Market Basics', [
        ('How Stock Markets Work', Lesson.VIDEO, 18, True),
        ('Types of Orders', Lesson.VIDEO, 15, False),
       ]),
      ('Module 2: Investing Basics', [
        ('Fundamental vs Technical Analysis', Lesson.VIDEO, 25, False),
        ('IPO Process Explained', Lesson.VIDEO, 20, False),
       ]),
     ]),
    ('Communication Skills for Finance Pros', 'Professional Skills', Course.BEGINNER, True, 0, 8,
     'Present finance like a pro',
     'Improve your business communication, presentation skills and client handling tailored for finance professionals.',
     [('Module 1: Communication', [
        ('Writing Effective Emails', Lesson.VIDEO, 12, True),
        ('Client Meetings', Lesson.VIDEO, 18, False),
       ]),
      ('Module 2: Presentations', [
        ('Building Financial Presentations', Lesson.VIDEO, 25, False),
        ('Handling Q&A', Lesson.VIDEO, 15, False),
       ]),
     ]),
    ('US CMA - Complete Preparation', 'Accounting', Course.ADVANCED, False, 4999, 60,
     'Complete US CMA coaching with practice tests',
     'Comprehensive preparation for the US CMA (Certified Management Accountant) exam Parts 1 and 2 with practice questions.',
     [('Part 1: Financial Planning', [
        ('External Financial Reporting Decisions', Lesson.VIDEO, 40, True),
        ('Planning & Budgeting', Lesson.VIDEO, 45, False),
        ('Performance Management', Lesson.VIDEO, 40, False),
        ('Cost Management', Lesson.VIDEO, 50, False),
        ('Internal Controls', Lesson.VIDEO, 30, False),
       ]),
      ('Part 2: Financial Decision', [
        ('Financial Statement Analysis', Lesson.VIDEO, 40, False),
        ('Corporate Finance', Lesson.VIDEO, 45, False),
        ('Decision Analysis', Lesson.VIDEO, 35, False),
        ('Risk Management', Lesson.VIDEO, 30, False),
        ('Investment Decisions', Lesson.VIDEO, 35, False),
        ('Mock Exam: Part 2', Lesson.QUIZ, 180, False),
       ]),
     ]),
    # ===== FinTech Accounting Track =====
    ('Payments Rails & Reconciliation', 'FinTech', Course.INTERMEDIATE, False, 1999, 22,
     'UPI, IMPS, NEFT settlement, NPCI files & gateway reconciliation',
     'A practitioner-led course on how fintech accountants reconcile payment flows across UPI/IMPS/NEFT, parse NPCI settlement files, and reconcile Stripe, Razorpay and PayPal payouts — including chargeback and refund accounting.',
     [('Module 1: Payment Rails & Settlement', [
        ('UPI, IMPS, NEFT, RTGS — How Money Actually Moves', Lesson.VIDEO, 22, True),
        ('NPCI Settlement Files — Reading the Daily NACH File', Lesson.VIDEO, 28, False),
        ('Reconciling Bank Float vs Payment Gateway Payouts', Lesson.VIDEO, 30, False),
       ]),
      ('Module 2: Gateway Reconciliation (Stripe / Razorpay / PayPal)', [
        ('Stripe Payouts, Fees & Application Fees — Line-by-Line', Lesson.VIDEO, 32, False),
        ('Razorpay Settlement Reports & TDR Reconciliation', Lesson.VIDEO, 28, False),
        ('PayPal IPN, Currency Conversion & Suspense Clearance', Lesson.VIDEO, 26, False),
        ('Assignment: Reconcile a 7-day gateway payout batch', Lesson.ASSIGNMENT, 90, False),
       ]),
      ('Module 3: Chargebacks, Refunds & Disputes', [
        ('Refund Accounting — Contra Entries & Reversal of Revenue', Lesson.VIDEO, 24, False),
        ('Chargeback Lifecycle & Provisioning for Disputes', Lesson.VIDEO, 22, False),
        ('Dispute Resolution Workflow & Tally/Journal Entries', Lesson.VIDEO, 20, False),
        ('Quiz: Payments Reconciliation Scenarios', Lesson.QUIZ, 20, False),
       ]),
     ]),
    ('SaaS & Subscription Billing Accounting', 'FinTech', Course.INTERMEDIATE, False, 2499, 26,
     'MRR/ARR recognition, deferred revenue, proration, dunning & ASC 606 / Ind AS 115',
     'Master subscription accounting for SaaS and fintech subscription products: MRR/ARR recognition, deferred revenue schedules, proration, dunning recoveries and revenue recognition under ASC 606 and Ind AS 115.',
     [('Module 1: Subscription Revenue Foundations', [
        ('MRR, ARR, NMRR — Definitions & Why They Matter', Lesson.VIDEO, 22, True),
        ('Deferred Revenue Schedules in Practice', Lesson.VIDEO, 28, False),
        ('Proration, Upgrades & Downgrades — Revenue Mechanics', Lesson.VIDEO, 26, False),
       ]),
      ('Module 2: ASC 606 / Ind AS 115 for Subscriptions', [
        ('The 5-Step Revenue Recognition Model', Lesson.VIDEO, 30, False),
        ('Identifying Performance Obligations in SaaS', Lesson.VIDEO, 26, False),
        ('Standalone Selling Price (SSP) Allocation', Lesson.VIDEO, 24, False),
       ]),
      ('Module 3: Dunning, Churn & Revenue Recovery', [
        ('Dunning Workflows — Failed Payments & Retries', Lesson.VIDEO, 22, False),
        ('Churn Accounting — Voluntary vs Involuntary', Lesson.VIDEO, 20, False),
        ('Contract Modifications & Refund Liabilities', Lesson.VIDEO, 24, False),
        ('Assignment: Build a 12-month deferred revenue schedule', Lesson.ASSIGNMENT, 120, False),
       ]),
     ]),
    ('Multi-Currency & FX Accounting', 'FinTech', Course.ADVANCED, False, 2999, 24,
     'Revaluation, gain/loss, hedge accounting & intercompany settlement',
     'A deep dive into multi-currency accounting for fintech operations: month-end revaluation, realised vs unrealised FX gain/loss, hedge accounting under Ind AS 109, and intercompany settlement across entities.',
     [('Module 1: FX Fundamentals for Accountants', [
        ('Spot, Forward & Swap Rates — The Treasurer\'s Toolkit', Lesson.VIDEO, 24, True),
        ('Functional vs Presentation Currency (Ind AS 21)', Lesson.VIDEO, 26, False),
        ('Initial vs Subsequent Measurement', Lesson.VIDEO, 22, False),
       ]),
      ('Module 2: Month-End Revaluation', [
        ('Monetary vs Non-Monetary Items', Lesson.VIDEO, 20, False),
        ('Realised vs Unrealised FX Gain/Loss', Lesson.VIDEO, 26, False),
        ('Revaluation Journals & Reversal in the Next Period', Lesson.VIDEO, 24, False),
        ('Assignment: Revalue a multi-currency trial balance', Lesson.ASSIGNMENT, 90, False),
       ]),
      ('Module 3: Hedge Accounting & Intercompany', [
        ('Cash Flow Hedges under Ind AS 109', Lesson.VIDEO, 32, False),
        ('Hedge Effectiveness Testing — Dollar Offset', Lesson.VIDEO, 28, False),
        ('Intercompany Settlement & Netting', Lesson.VIDEO, 26, False),
        ('Quiz: FX Scenarios for a Cross-Border Fintech', Lesson.QUIZ, 25, False),
       ]),
     ]),
    ('Crypto & Digital Assets Accounting', 'FinTech', Course.ADVANCED, False, 3499, 28,
     'On-chain transaction accounting, cost-basis, stablecoins, IFRS stance & taxation',
     'A specialised course on accounting for cryptoassets: on-chain transaction accounting, FIFO/Specific-ID cost-basis tracking, stablecoin settlement, IFRIC stance on holdings, and taxation of crypto gains in India.',
     [('Module 1: On-Chain Transaction Accounting', [
        ('Wallets, UTXOs & Account Model — A Primer for Accountants', Lesson.VIDEO, 26, True),
        ('Reading a Blockchain Explorer as a Source Document', Lesson.VIDEO, 24, False),
        ('Reconciling On-Chain Activity to the General Ledger', Lesson.VIDEO, 30, False),
       ]),
      ('Module 2: Cost-Basis & Stablecoins', [
        ('FIFO vs Specific Identification (Ind AS 2 / IAS 2)', Lesson.VIDEO, 28, False),
        ('Stablecoin Settlement & Tokenised Treasury', Lesson.VIDEO, 26, False),
        ('Trading vs Investment Classification', Lesson.VIDEO, 22, False),
        ('Assignment: Track cost-basis across 50 trades', Lesson.ASSIGNMENT, 100, False),
       ]),
      ('Module 3: IFRS Stance & Indian Taxation', [
        ('IFRIC & IFRS Interpretations on Crypto Holdings', Lesson.VIDEO, 28, False),
        ('India — 30% Flat Tax & 1% TDS on Crypto Transfers', Lesson.VIDEO, 26, False),
        ('Reporting, Disclosure & Audit Trail Requirements', Lesson.VIDEO, 24, False),
        ('Quiz: Crypto Accounting & Tax Scenarios', Lesson.QUIZ, 25, False),
       ]),
     ]),
    ('Lending & BNPL Accounting', 'FinTech', Course.ADVANCED, False, 2999, 26,
     'NPA recognition, EIR/AMORT, securitisation & write-offs',
     'Accounting for digital lending and BNPL portfolios: EIR/AMORT schedule construction, NPA recognition under RBI norms, securitisation and assignment of loans, and write-off/recovery accounting.',
     [('Module 1: Loan Origination & EIR', [
        ('Effective Interest Rate (EIR) Method Explained', Lesson.VIDEO, 28, True),
        ('AMORT Schedule Construction in Excel', Lesson.VIDEO, 32, False),
        ('Processing Fees, Pre-EMI & Disbursal Entries', Lesson.VIDEO, 26, False),
       ]),
      ('Module 2: NPA Recognition & Provisioning', [
        ('RBI NPA Norms — DPD, SMA-0/1/2, NPA', Lesson.VIDEO, 30, False),
        ('Standard, Sub-Standard, Doubtful & Loss Asset Provisioning', Lesson.VIDEO, 28, False),
        ('Write-Off & Recovery Accounting', Lesson.VIDEO, 24, False),
        ('Assignment: Build a provisioning schedule', Lesson.ASSIGNMENT, 90, False),
       ]),
      ('Module 3: Securitisation & BNPL Specifics', [
        ('Securitisation & Assignment of Loans — Accounting', Lesson.VIDEO, 28, False),
        ('BNPL Merchant Subvention & Revenue Split', Lesson.VIDEO, 24, False),
        ('Late Fees, Collection Costs & IBC Recoveries', Lesson.VIDEO, 22, False),
        ('Quiz: Lending & BNPL Scenarios', Lesson.QUIZ, 25, False),
       ]),
     ]),
    ('Embedded Finance & BaaS Accounting', 'FinTech', Course.ADVANCED, False, 2999, 24,
     'Ledger-as-a-service, virtual account reconciliation & float accounting',
     'Accounting for embedded finance and Banking-as-a-Service: ledger-as-a-service design, virtual account reconciliation, float and customer money accounting, and partner-bank settlement mechanics.',
     [('Module 1: Ledger-as-a-Service Foundations', [
        ('What is a Ledger-as-a-Service (LaaS)?', Lesson.VIDEO, 22, True),
        ('Double-Entry vs Event-Sourced Ledgers', Lesson.VIDEO, 26, False),
        ('Idempotency, Reversals & Compensating Entries', Lesson.VIDEO, 24, False),
       ]),
      ('Module 2: Virtual Accounts & Customer Money', [
        ('Virtual Account Lifecycle & Mapping to Customers', Lesson.VIDEO, 26, False),
        ('Customer Money vs Operating Float — Segregation', Lesson.VIDEO, 28, False),
        ('Trust Accounts, Escrow & Ind AS 105 Considerations', Lesson.VIDEO, 26, False),
        ('Assignment: Reconcile 1000 virtual accounts', Lesson.ASSIGNMENT, 90, False),
       ]),
      ('Module 3: Partner-Bank Settlement', [
        ('Reconciling Partner-Bank Settlements', Lesson.VIDEO, 26, False),
        ('NPCI & Sponsor-Bank Reporting', Lesson.VIDEO, 22, False),
        ('Revenue Share, Interchange & Pass-Through Accounting', Lesson.VIDEO, 24, False),
        ('Quiz: BaaS Reconciliation Scenarios', Lesson.QUIZ, 20, False),
       ]),
     ]),
    ('RegTech & Compliance Automation', 'FinTech', Course.INTERMEDIATE, False, 1999, 20,
     'KYC/AML accounting, FEMA reporting, DIN/PAN validation',
     'A course on the accounting and reporting side of RegTech: automating KYC/AML provisioning, FEMA reporting for cross-border transactions, DIN/PAN validation workflows, and audit-trail automation.',
     [('Module 1: KYC/AML Accounting', [
        ('KYC Cost Allocation & Vendor Reconciliation', Lesson.VIDEO, 22, True),
        ('AML Alert Provisioning & Investigation Cost', Lesson.VIDEO, 24, False),
        ('Penalty & Fine Accounting under PMLA', Lesson.VIDEO, 22, False),
       ]),
      ('Module 2: FEMA & Cross-Border Reporting', [
        ('FEMA Reporting — FIRC, e-FIRC & R-Returns', Lesson.VIDEO, 28, False),
        ('ECB, Trade & FDI Accounting Triggers', Lesson.VIDEO, 26, False),
        ('Reconciling FEMA Filings with the GL', Lesson.VIDEO, 24, False),
       ]),
      ('Module 3: DIN/PAN & Audit Trail Automation', [
        ('DIN Generation & Validation Workflow', Lesson.VIDEO, 22, False),
        ('PAN-Aadhaar Linking & Section 206AA/206CC', Lesson.VIDEO, 24, False),
        ('Audit Trail under Section 44AA & Rule 11', Lesson.VIDEO, 22, False),
        ('Assignment: Build a compliance reconciliation checklist', Lesson.ASSIGNMENT, 80, False),
       ]),
     ]),
    ('Fintech FP&A — Unit Economics, Burn & Treasury', 'FinTech', Course.ADVANCED, False, 2499, 25,
     'CAC/LTV, burn & runway, treasury ops for fintech startups',
     'Financial Planning & Analysis tailored to fintech startups: unit economics (CAC, LTV, payback), burn & runway modelling, scenario planning, and treasury operations including liquidity sweeps and investment of idle cash.',
     [('Module 1: Unit Economics for Fintech', [
        ('CAC, LTV & Payback Period — The Fintech Lens', Lesson.VIDEO, 26, True),
        ('Cohort Analysis & Retention Curves', Lesson.VIDEO, 28, False),
        ('Contribution Margin per Transaction', Lesson.VIDEO, 24, False),
       ]),
      ('Module 2: Burn, Runway & Fundraise Modelling', [
        ('Monthly Burn — Cash vs Accrual', Lesson.VIDEO, 24, False),
        ('Runway Scenarios & Fundraise Timing', Lesson.VIDEO, 26, False),
        ('Cap Table & Dilution in FP&A Models', Lesson.VIDEO, 28, False),
        ('Assignment: Build a 36-month operating model', Lesson.ASSIGNMENT, 120, False),
       ]),
      ('Module 3: Treasury Operations', [
        ('Liquidity Sweeps & Idle Cash Deployment', Lesson.VIDEO, 24, False),
        ('Investment Policy Statement for Startups', Lesson.VIDEO, 22, False),
        ('Counterparty Risk & Bank Exposure Limits', Lesson.VIDEO, 22, False),
        ('Quiz: FP&A & Treasury Scenarios', Lesson.QUIZ, 25, False),
       ]),
     ]),
]


# Jobs: (title, category_name, emp_idx, type, exp, city, state, remote, wfh, sal_min, sal_max, skills, featured)
JOBS = [
    ('Senior Accountant', 'Senior Accountant', 0, Job.FULL_TIME, 'mid', 'Mumbai', 'Maharashtra', False, False, 800000, 1200000, 'Tally Prime, GST, Final Accounts, Audit', True),
    ('GST Executive', 'GST Executive', 0, Job.FULL_TIME, 'entry', 'Mumbai', 'Maharashtra', False, False, 350000, 500000, 'GST, TDS, Tally', False),
    ('Tax Consultant', 'Tax Consultant', 1, Job.FULL_TIME, 'mid', 'Delhi', 'Delhi', True, True, 600000, 900000, 'Income Tax, GST, Advisory', True),
    ('Accounts Manager', 'Accounts Manager', 0, Job.FULL_TIME, 'senior', 'Pune', 'Maharashtra', False, False, 1000000, 1500000, 'Accounts, Audit, Team Management', True),
    ('Financial Analyst', 'Financial Analyst', 1, Job.FULL_TIME, 'mid', 'Bengaluru', 'Karnataka', True, True, 700000, 1100000, 'Excel, Financial Modelling, Analysis', True),
    ('Audit Assistant', 'Audit Assistant', 0, Job.FULL_TIME, 'entry', 'Chennai', 'Tamil Nadu', False, False, 400000, 550000, 'Audit, Accounting', False),
    ('Banking Executive', 'Banking Executive', 1, Job.FULL_TIME, 'entry', 'Hyderabad', 'Telangana', False, False, 380000, 520000, 'Banking, Customer Service', False),
    ('FinTech Developer', 'FinTech Developer', 1, Job.FULL_TIME, 'mid', 'Bengaluru', 'Karnataka', True, True, 1200000, 2000000, 'Python, Django, APIs, FinTech', True),
    ('Financial Modelling Analyst', 'Financial Modelling Analyst', 1, Job.FULL_TIME, 'mid', 'Mumbai', 'Maharashtra', True, True, 900000, 1400000, 'Excel, Financial Modelling, Valuation', True),
    ('Tally Operator', 'Tally Operator', 0, Job.PART_TIME, 'entry', 'Ahmedabad', 'Gujarat', False, False, 250000, 350000, 'Tally Prime, Data Entry', False),
    ('Internship - Accounting', 'Accountant', 0, Job.INTERNSHIP, 'entry', 'Pune', 'Maharashtra', True, True, 150000, 250000, 'Accounting, Excel', False),
    ('Freelance - GST Returns', 'GST Executive', 1, Job.FREELANCE, 'mid', 'Remote', 'India', True, True, 200000, 400000, 'GST, TDS', False),
    # ===== FinTech-specific roles =====
    ('Payments Accountant', 'Payments Accountant', 12, Job.FULL_TIME, 'mid', 'Bengaluru', 'Karnataka', True, True, 900000, 1400000, 'UPI, NPCI, Payment Gateway Reconciliation, Razorpay, Stripe', True),
    ('Revenue Accountant (SaaS)', 'Revenue Accountant', 13, Job.FULL_TIME, 'mid', 'Bengaluru', 'Karnataka', True, True, 1100000, 1700000, 'MRR/ARR, Deferred Revenue, ASC 606, Ind AS 115, Subscription Billing', True),
    ('Crypto Operations Accountant', 'Crypto Operations Accountant', 14, Job.FULL_TIME, 'mid', 'Remote', 'India', True, True, 1500000, 2400000, 'On-Chain Reconciliation, Cost-Basis, Stablecoins, 30% Tax, 1% TDS', True),
    ('Reconciliation Analyst - Fintech', 'Reconciliation Analyst', 15, Job.FULL_TIME, 'entry', 'Mumbai', 'Maharashtra', False, True, 600000, 900000, 'Bank Reconciliation, Gateway Settlement, Suspense Clearance, Excel', False),
    ('Treasury Analyst - Fintech', 'Treasury Analyst', 16, Job.FULL_TIME, 'mid', 'Hyderabad', 'Telangana', True, True, 1000000, 1500000, 'FX Revaluation, Hedge Accounting, Liquidity, Intercompany, Treasury Management System', True),
]


def run():
    # ---- Roles ----
    for code, _ in Role.ROLE_CHOICES:
        Role.objects.get_or_create(name=code)
    print('Roles:', Role.objects.count())

    # ---- Users ----
    admin = _user('admin@fintechaccountant.com', 'Admin', 'User', ['admin'],
                  headline='Platform Administrator', city='Mumbai', is_staff=True, is_superuser=True)
    admin.is_staff = True; admin.is_superuser = True; admin.save()

    student = _user('student@demo.in', 'Priya', 'Sharma', ['student'],
                    headline='B.Com Final Year', city='Mumbai', state='Maharashtra',
                    bio='Final year B.Com student aspiring to become a CA. Learning GST and Tally.')
    prof = _user('ca@demo.in', 'Rajesh', 'Iyer', ['professional', 'accountant'],
                 headline='CA | 8 yrs in Audit & GST', city='Bengaluru', state='Karnataka',
                 bio='Chartered Accountant with experience in audit, GST and indirect taxation.')
    instructor1 = _user('instructor@demo.in', 'Meera', 'Nair', ['instructor', 'professional'],
                         headline='CMA | Finance Trainer', city='Chennai', state='Tamil Nadu',
                         bio='CMA with 15+ years training accountants in cost accounting and financial modelling.')
    instructor2 = _user('rajesh@demo.in', 'Rajesh', 'Kumar', ['instructor', 'professional'],
                        headline='GST Expert & Trainer', city='Hyderabad', state='Telangana',
                        bio='GST practitioner and trainer with 10+ years experience.')
    instructor3 = _user('fintech.instructor@demo.in', 'Anjali', 'Verma', ['instructor', 'professional'],
                        headline='FinTech Accountant | Ex-Razorpay, Ex-PayPal', city='Bengaluru', state='Karnataka',
                        bio='CA with 12+ years in payments, SaaS revenue, crypto and BNPL accounting at leading Indian fintechs.')
    emp1 = _user('hr@acme.in', 'Acme', 'HR', ['employer'],
                 headline='Recruiter at Acme Corp', city='Pune', state='Maharashtra')
    emp2 = _user('careers@finovate.in', 'Finovate', 'HR', ['employer'],
                 headline='Talent Acquisition at Finovate', city='Bengaluru', state='Karnataka')
    print('Users:', User.objects.count())

    # ---- Instructor profiles ----
    InstructorProfile.objects.get_or_create(
        user=instructor1, defaults={'title': 'CMA | Finance Trainer', 'bio': '15+ years training accountants.',
                                      'expertise': 'CMA, Cost Accounting, Financial Modelling', 'years_teaching': 15})
    InstructorProfile.objects.get_or_create(
        user=instructor2, defaults={'title': 'GST Expert & Trainer', 'bio': 'GST practitioner and trainer.',
                                      'expertise': 'GST, TDS, Indirect Taxation', 'years_teaching': 10})
    InstructorProfile.objects.get_or_create(
        user=instructor3, defaults={'title': 'FinTech Accountant | Ex-Razorpay, Ex-PayPal',
                                      'bio': 'Chartered Accountant with 12+ years in payments, SaaS revenue and crypto accounting at leading Indian fintechs.',
                                      'expertise': 'Payments Reconciliation, SaaS Revenue, Crypto Accounting, Multi-Currency, BNPL, BaaS, RegTech, Fintech FP&A',
                                      'years_teaching': 12})
    print('Instructor profiles:', InstructorProfile.objects.count())

    # ---- Employer profiles ----
    EmployerProfile.objects.get_or_create(
        user=emp1, defaults={'company_name': 'Acme Corp', 'industry': 'Manufacturing & Finance',
                              'company_size': '201-1000', 'headquarters_city': 'Pune',
                              'about': 'A leading manufacturer with a growing finance team.'})
    EmployerProfile.objects.get_or_create(
        user=emp2, defaults={'company_name': 'Finovate Solutions', 'industry': 'FinTech',
                              'company_size': '51-200', 'headquarters_city': 'Bengaluru',
                              'about': 'Building the next generation of digital payment solutions.'})
    print('Employer profiles:', EmployerProfile.objects.count())

    # ---- Skills ----
    for s in ['GST', 'Tally Prime', 'Income Tax', 'Excel', 'Financial Modelling',
              'Python', 'Django', 'Auditing', 'TDS', 'Cost Accounting',
              'Valuation', 'Banking', 'Digital Payments', 'Stock Market', 'Communication',
              # FinTech-track skills
              'UPI', 'NPCI Settlement', 'Payment Gateway Reconciliation', 'Razorpay', 'Stripe',
              'MRR/ARR', 'Deferred Revenue', 'ASC 606', 'Ind AS 115', 'Subscription Billing',
              'FX Revaluation', 'Hedge Accounting', 'Intercompany Settlement',
              'On-Chain Reconciliation', 'Cost-Basis Tracking', 'Stablecoins', 'Crypto Taxation',
              'EIR/AMORT', 'NPA Recognition', 'Securitisation', 'BNPL Accounting',
              'Ledger-as-a-Service', 'Virtual Account Reconciliation', 'Float Accounting',
              'KYC/AML', 'FEMA Reporting', 'DIN/PAN Validation',
              'CAC/LTV', 'Burn & Runway', 'Treasury Operations']:
        Skill.objects.get_or_create(name=s)
    print('Skills:', Skill.objects.count())

    # Attach some skills to the student and CA profile
    for name, level in [('GST', 'intermediate'), ('Tally Prime', 'beginner'), ('Excel', 'intermediate')]:
        skill = Skill.objects.get(name=name)
        ProfileSkill.objects.get_or_create(profile=student.profile, skill=skill, defaults={'level': level})
    for name, level in [('GST', 'expert'), ('TDS', 'expert'), ('Auditing', 'expert'), ('Excel', 'advanced')]:
        skill = Skill.objects.get(name=name)
        ProfileSkill.objects.get_or_create(profile=prof.profile, skill=skill, defaults={'level': level})

    # ---- Course categories ----
    cats_spec = ['Accounting', 'Taxation', 'Software', 'Finance', 'FinTech',
                 'Technology', 'Capital Markets', 'Professional Skills']
    for c in cats_spec:
        Category.objects.get_or_create(name=c)
    print('Course categories:', Category.objects.count())

    # ---- Courses ----
    instructors = [instructor1, instructor1, instructor2, instructor1, instructor1,
                   instructor2, instructor2, instructor1, instructor2, instructor1,
                   instructor1, instructor1,
                   # 8 FinTech-track courses — taught by the fintech-specialist instructor
                   instructor3, instructor3, instructor3, instructor3,
                   instructor3, instructor3, instructor3, instructor3]
    for idx, (title, cat_name, level, is_free, price, hours, subtitle, desc, modules_data) in enumerate(COURSES):
        cat = Category.objects.get(name=cat_name)
        instructor = instructors[idx] if idx < len(instructors) else instructor1
        course, created = Course.objects.get_or_create(
            title=title,
            defaults={'subtitle': subtitle, 'description': desc, 'category': cat,
                      'level': level, 'delivery': Course.RECORDED, 'status': Course.PUBLISHED,
                      'instructor': instructor, 'is_free': is_free, 'price': price,
                      'duration_hours': hours, 'is_featured': idx < 4, 'students_count': 50 + idx * 20}
        )
        if not created:
            continue
        for m_idx, (m_title, lessons_data) in enumerate(modules_data, 1):
            module, _ = Module.objects.get_or_create(course=course, title=m_title, defaults={'order': m_idx})
            for l_idx, (l_title, l_type, mins, preview) in enumerate(lessons_data, 1):
                Lesson.objects.get_or_create(module=module, title=l_title,
                    defaults={'content_type': l_type, 'duration_minutes': mins,
                              'is_preview': preview, 'order': l_idx,
                              'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' if l_type == Lesson.VIDEO else '',
                              'body': desc[:200] if l_type == Lesson.READING else ''})
    print('Courses:', Course.objects.count(), 'Modules:', Module.objects.count(), 'Lessons:', Lesson.objects.count())

    # ---- Job categories ----
    job_cats = ['Accountant', 'Senior Accountant', 'GST Executive', 'Tax Consultant',
                'Accounts Manager', 'Financial Analyst', 'Audit Assistant',
                'Banking Executive', 'FinTech Developer', 'Financial Modelling Analyst',
                'Tally Operator', 'CFO / Finance Controller',
                # FinTech-specific job categories
                'Payments Accountant', 'Revenue Accountant',
                'Crypto Operations Accountant', 'Reconciliation Analyst',
                'Treasury Analyst']
    for c in job_cats:
        JobCategory.objects.get_or_create(name=c)
    print('Job categories:', JobCategory.objects.count())

    # ---- Jobs ----
    emps = [emp1.employer_profile, emp1.employer_profile, emp2.employer_profile,
            emp1.employer_profile, emp2.employer_profile, emp1.employer_profile,
            emp2.employer_profile, emp2.employer_profile, emp2.employer_profile,
            emp1.employer_profile, emp1.employer_profile, emp2.employer_profile,
            # 5 FinTech-specific roles — all at Finovate (fintech employer)
            emp2.employer_profile, emp2.employer_profile, emp2.employer_profile,
            emp2.employer_profile, emp2.employer_profile]
    for idx, (title, cat_name, emp_idx, jtype, exp, city, state, remote, wfh, sal_min, sal_max, skills, featured) in enumerate(JOBS):
        cat = JobCategory.objects.get(name=cat_name)
        employer = emps[emp_idx]
        posted_by = employer.user
        import re
        slug_base = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        slug = f'{slug_base}-{idx+1}'
        Job.objects.get_or_create(
            slug=slug,
            defaults={'title': title,
                      'description': f'We are hiring a {title} to join our growing team. This is an excellent opportunity for finance professionals.',
                      'requirements': f'Relevant qualification and experience. Skills: {skills}.',
                      'responsibilities': 'Manage day-to-day finance operations and reporting.',
                      'employer': employer, 'posted_by': posted_by, 'category': cat,
                      'employment_type': jtype, 'experience_level': exp,
                      'location_city': city, 'location_state': state,
                      'is_remote': remote, 'is_wfh': wfh,
                      'salary_min': sal_min, 'salary_max': sal_max, 'is_salary_disclosed': True,
                      'skills_required': skills, 'status': Job.OPEN, 'openings': 2,
                      'is_featured': featured,
                      'application_deadline': timezone.now() + timedelta(days=30)})
    print('Jobs:', Job.objects.count())

    # ---- Communities ----
    comms = [
        ('Chartered Accountants Network', 'Accounting', prof),
        ('GST Practitioners Community', 'Taxation', prof),
        ('Tally & Accounting Professionals', 'Software', prof),
        ('Banking & Financial Services', 'Banking', prof),
        ('FinTech Developers', 'FinTech', instructor1),
        ('Investment & Capital Markets', 'Investment', prof),
        ('Excel and Financial Modelling', 'Software', instructor1),
        ('Finance Students Community', 'Students', student),
        ('CA Final Aspirants', 'Accounting', student),
        ('CMA Professionals', 'Accounting', instructor1),
        # FinTech-accountant-specific communities
        ('FinTech Accountants & Controllers', 'FinTech', instructor3),
        ('Crypto & Digital Assets Accounting', 'FinTech', instructor3),
        ('SaaS Revenue Accounting', 'FinTech', instructor3),
        ('Payments & Reconciliation Ops', 'FinTech', instructor3),
    ]
    for idx, (name, cat, owner) in enumerate(comms):
        Community.objects.get_or_create(
            name=name,
            defaults={'description': f'A community for {name.lower()}.',
                      'category': cat,
                      'is_official': idx < 8,
                      'owner': owner,
                      'members_count': 50 + idx * 25})
    print('Communities:', Community.objects.count())

    # ---- Events ----
    events_data = [
        ('GST Updates 2026: What is New', Event.WEBINAR, timezone.now() + timedelta(days=7), True, 0, instructor2),
        ('Career Paths in FinTech', Event.WEBINAR, timezone.now() + timedelta(days=14), True, 0, instructor1),
        ('Excel Masterclass Live', Event.WORKSHOP, timezone.now() + timedelta(days=21), False, 499, instructor1),
        ('CA Campus Placement Bootcamp', Event.WORKSHOP, timezone.now() + timedelta(days=30), False, 999, prof),
        # FinTech-accountant-focused events
        ('Payments Reconciliation Bootcamp', Event.WORKSHOP, timezone.now() + timedelta(days=10), False, 799, instructor3),
        ('Crypto Accounting & 30% Tax Workshop', Event.WEBINAR, timezone.now() + timedelta(days=18), True, 0, instructor3),
    ]
    for title, etype, starts, is_paid, price, organiser in events_data:
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:60]
        Event.objects.get_or_create(
            slug=slug,
            defaults={'title': title,
                      'description': f'Join us for {title.lower()}.',
                      'event_type': etype, 'status': Event.PUBLISHED,
                      'starts_at': starts, 'ends_at': starts + timedelta(hours=2),
                      'is_online': True, 'meeting_url': 'https://meet.example.com/' + slug,
                      'organiser': organiser, 'max_attendees': 100,
                      'is_paid': is_paid, 'price': price, 'is_featured': True})
    print('Events:', Event.objects.count())

    print('\n=== Seed complete ===')
    print('Demo logins (password: demo1234, admin: admin123):')
    print('  admin@fintechaccountant.com / admin123')
    print('  student@demo.in')
    print('  ca@demo.in')
    print('  instructor@demo.in')
    print('  rajesh@demo.in')
    print('  hr@acme.in')
    print('  careers@finovate.in')


if __name__ == '__main__':
    run()
