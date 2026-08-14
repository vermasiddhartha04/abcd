def generate_reply(
    metadata: dict,
    analysis: dict,
):
    taxpayer = metadata.get("taxpayer_name") or "Taxpayer"
    notice = metadata.get("notice_number") or "N/A"
    section = metadata.get("section") or "N/A"
    fy = metadata.get("financial_year") or "N/A"

    summary = analysis.get("summary") or ""
    recommendation = analysis.get("recommendation") or ""

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
The taxpayer respectfully submits that all GST provisions have been complied with. Relevant books of accounts, invoices, returns and supporting documents shall be produced before the department.

4. Recommendation
-----------------
{recommendation}

5. Prayer
----------
It is humbly requested that the proposed demand, if any, may kindly be dropped after considering the submissions and supporting evidence.

Thanking You,

Authorized Signatory
"""

    return reply.strip()