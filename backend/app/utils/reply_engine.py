def generate_reply(
    metadata: dict,
    analysis: dict,
    document_type: str = "SCN",
):
    taxpayer = (
        metadata.get("taxpayer_name")
        or "Taxpayer"
    )

    notice = (
        metadata.get("notice_number")
        or "N/A"
    )

    section = (
        metadata.get("section")
        or "N/A"
    )

    fy = (
        metadata.get("financial_year")
        or "N/A"
    )

    summary = (
        analysis.get("summary")
        or ""
    )

    recommendation = (
        analysis.get("recommendation")
        or ""
    )

    # ========================================================
    # SCN REPLY
    # ========================================================

    if document_type == "SCN":

        reply = f"""
To,
The Proper Officer

Subject: Reply to Show Cause Notice No. {notice}

Respected Sir/Madam,

With due respect, we hereby submit our reply against the Show Cause Notice issued under Section {section} of the CGST Act.

1. Facts of the Case
--------------------
The notice pertains to {taxpayer} for the Financial Year {fy}.

2. Summary
----------
{summary}

3. Submission
-------------
The taxpayer respectfully submits that the allegations and proposed demand may kindly be examined in light of the books of accounts, tax invoices, GST returns, reconciliation statements, payment records and other supporting documents.

The taxpayer reserves the right to submit additional documents and explanations wherever required.

4. Legal and Factual Submission
--------------------------------
The issues mentioned in the notice should be examined section-wise with reference to the actual transactions, applicable GST provisions, returns filed and supporting records.

5. Recommendation / Supporting Evidence
---------------------------------------
{recommendation}

Relevant invoices, books of accounts, GSTR-1, GSTR-3B, GSTR-2A/2B reconciliation, payment records and other supporting documents should be attached wherever applicable.

6. Prayer
---------
In view of the facts, explanations and supporting evidence, it is respectfully requested that the proposed demand may kindly be reconsidered and dropped to the extent legally and factually justified.

Thanking You,

Authorized Signatory
{taxpayer}
"""

        return reply.strip()

    # ========================================================
    # OIO → APPEAL DRAFT
    # ========================================================

    if document_type == "OIO":

        reply = f"""
BEFORE THE APPELLATE AUTHORITY

MEMORANDUM / DRAFT GROUNDS OF APPEAL

Appellant:
{taxpayer}

Reference / OIO Number:
{notice}

Financial Year:
{fy}

1. Background
--------------
The present appeal is proposed against the Order-in-Original passed in the matter of {taxpayer}.

2. Order Under Challenge
------------------------
The impugned Order-in-Original and the findings recorded therein require examination with reference to the Show Cause Notice, taxpayer's earlier submissions and supporting evidence.

3. Grounds of Appeal
--------------------
The appellant proposes to challenge the findings of the Order-in-Original on facts and law.

The demand, interest and penalty, wherever applicable, should be examined with reference to the actual transaction records, GST returns, invoices, reconciliation statements and other documentary evidence.

4. Supporting Documents
------------------------
The appellant should provide the relevant:

- Show Cause Notice
- Order-in-Original
- SCN Reply
- Tax invoices
- Books of accounts
- GSTR-1
- GSTR-3B
- GSTR-2A / GSTR-2B reconciliation
- Payment records
- Other relevant evidence

5. Relief Sought
----------------
It is respectfully requested that the findings and demand confirmed under the Order-in-Original may kindly be examined and appropriate relief may be granted in accordance with law.

6. Conclusion
-------------
{recommendation}

Place:
Date:

Authorized Signatory
{taxpayer}
"""

        return reply.strip()

    # ========================================================
    # APPEAL → OIA STAGE
    # ========================================================

    if document_type == "APPEAL":

        reply = f"""
APPEAL REVIEW / OIA STAGE NOTE

Taxpayer:
{taxpayer}

Appeal Reference:
{notice}

Financial Year:
{fy}

1. Appeal Summary
-----------------
{summary}

2. Grounds Under Review
-----------------------
The grounds of appeal should be examined against the challenged Order-in-Original, supporting evidence and applicable GST provisions.

3. Documents for Appellate Review
---------------------------------
The following documents should be kept available:

- Order-in-Original
- Memorandum of Appeal
- Grounds of Appeal
- SCN
- SCN Reply
- Tax invoices
- GST returns
- Reconciliation statements
- Payment records
- Other supporting evidence

4. Next Stage
-------------
The matter is now at the appellate stage and may proceed towards an Order-in-Appeal (OIA).

5. Recommendation
-----------------
{recommendation}

Final appellate outcome should be reviewed once the Order-in-Appeal is issued.
"""

        return reply.strip()

    # ========================================================
    # OIA → FINAL REVIEW
    # ========================================================

    if document_type == "OIA":

        return f"""
FINAL OIA REVIEW

Taxpayer:
{taxpayer}

Reference:
{notice}

Financial Year:
{fy}

Summary:
{summary}

Recommendation:
{recommendation}

The Order-in-Appeal should be reviewed to determine whether the Order-in-Original was upheld, modified or set aside.

Further legal remedy, if any, should be determined after reviewing the final findings and applicable procedure.
""".strip()

    # ========================================================
    # FALLBACK
    # ========================================================

    return f"""
DOCUMENT REVIEW

Taxpayer:
{taxpayer}

Reference:
{notice}

Financial Year:
{fy}

Summary:
{summary}

Recommendation:
{recommendation}
""".strip()