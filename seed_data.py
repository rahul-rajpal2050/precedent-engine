"""
Seed script — populates ChromaDB with 3 historical tech MSA contracts.
Run once: python seed_data.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.database import upsert_precedents

CONTRACTS = {
    "MSA-2022-ACME": """
MASTER SOFTWARE SERVICES AGREEMENT

WHEREAS, Acme Corp ("Customer") desires to obtain software services from Vendor;
NOW THEREFORE, the parties agree as follows:

SECTION 1 – PAYMENT
Customer shall pay all invoices within thirty (30) days of the invoice date (Net-30). Late payments accrue interest at 1.5% per month.

SECTION 2 – LIMITATION OF LIABILITY
In no event shall either party's aggregate liability arising out of or related to this Agreement exceed the total fees paid by Customer to Vendor in the twelve (12) months preceding the claim. In cases of data breach, liability is capped at two times (2x) the total contract value paid in the prior 12 months. Neither party shall be liable for any indirect, incidental, or consequential damages.

SECTION 3 – GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the State of New York, without regard to its conflict of laws principles. Any disputes shall be resolved exclusively in the courts located in New York County, New York.

SECTION 4 – INDEMNIFICATION
Each party ("Indemnifying Party") shall indemnify, defend, and hold harmless the other party from any third-party claims arising out of the Indemnifying Party's gross negligence or willful misconduct. Vendor shall indemnify Customer against claims that the software infringes a third-party intellectual property right; Customer shall provide reciprocal IP indemnification for any modifications it makes.

SECTION 5 – TERM AND TERMINATION
This Agreement commences on the Effective Date and continues for one (1) year, automatically renewing for successive one-year terms unless either party provides written notice of non-renewal at least thirty (30) days prior to the end of the then-current term.

SECTION 6 – ASSIGNMENT
Neither party may assign or transfer this Agreement or any rights hereunder without the prior written consent of the other party, which shall not be unreasonably withheld.
""",

    "MSA-2023-GLOBEX": """
MASTER SERVICES AGREEMENT — GLOBEX TECHNOLOGIES

SECTION 1 – FEES AND PAYMENT
All fees are due within forty-five (45) days of invoice date (Net-45). Vendor reserves the right to suspend services for payments overdue by more than fifteen (15) days.

SECTION 2 – LIMITATION OF LIABILITY
Vendor's total cumulative liability for any and all claims under this Agreement shall not exceed the greater of (a) USD $500,000 or (b) the fees paid by Customer in the six (6) months preceding the event giving rise to liability. This limitation applies regardless of the theory of liability, including but not limited to contract, tort, or strict liability. Liability for data breaches involving Customer's personal data shall be capped at two times (2x) contract value paid in the prior 12 months.

SECTION 3 – GOVERNING LAW AND DISPUTE RESOLUTION
This Agreement is governed by the laws of the State of New York. The parties agree to submit to binding arbitration under AAA Commercial Arbitration Rules before initiating any litigation.

SECTION 4 – CONFIDENTIALITY
Each party agrees to maintain the confidentiality of the other party's proprietary information and not to disclose such information to any third party without prior written consent. Obligations survive termination for five (5) years.

SECTION 5 – INTELLECTUAL PROPERTY INDEMNIFICATION
Vendor shall defend and indemnify Customer against third-party claims alleging that Vendor's software infringes any patent, copyright, or trademark. Customer shall provide equivalent indemnification for any Customer-provided materials integrated into deliverables.

SECTION 6 – FORCE MAJEURE
Neither party shall be liable for delays caused by circumstances beyond its reasonable control, including acts of God, government actions, or telecommunications failures, provided the affected party gives prompt written notice.
""",

    "MSA-2024-INITECH": """
MASTER SOFTWARE SUBSCRIPTION AGREEMENT — INITECH INC

1. SUBSCRIPTION FEES
Customer shall pay subscription fees within sixty (60) days of invoice (Net-60). Vendor may charge a late fee of 2% per month on overdue balances.

2. LIABILITY LIMITATIONS
THE MAXIMUM AGGREGATE LIABILITY OF EITHER PARTY FOR ANY CLAIMS ARISING UNDER THIS AGREEMENT SHALL NOT EXCEED THE AMOUNTS PAID BY CUSTOMER IN THE THREE (3) MONTHS PRECEDING THE CLAIM. NOTWITHSTANDING THE FOREGOING, THERE SHALL BE NO CAP ON LIABILITY FOR: (A) DEATH OR PERSONAL INJURY, (B) FRAUD, OR (C) ANY DATA BREACH RESULTING FROM VENDOR'S WILLFUL MISCONDUCT. This clause represents a negotiated outcome and Customer acknowledges the limitation is a material basis for pricing.

3. GOVERNING LAW
This Agreement is governed by the laws of the State of Delaware. The parties consent to exclusive jurisdiction of the courts of Delaware for any disputes not resolved through mediation.

4. TERM AND RENEWAL
The initial term is two (2) years. This Agreement automatically renews for one (1) year periods. Either party may prevent renewal by providing sixty (60) days' written notice prior to the end of the current term.

5. INDEMNIFICATION
Vendor indemnifies Customer against third-party IP infringement claims related solely to the unmodified software. Customer indemnification obligations are limited to claims arising from Customer's gross negligence.

6. ASSIGNMENT
Customer may assign this Agreement in connection with a merger, acquisition, or sale of substantially all assets without Vendor's consent, provided the assignee assumes all obligations hereunder.
""",
}


def main():
    from core.parser import chunk_contract

    total = 0
    for contract_id, text in CONTRACTS.items():
        chunks = chunk_contract(text)
        count = upsert_precedents(contract_id, chunks)
        total += count
        print(f"  Seeded {contract_id}: {count} chunks")

    print(f"\nDone. Total chunks in ChromaDB: {total}")


if __name__ == "__main__":
    main()
