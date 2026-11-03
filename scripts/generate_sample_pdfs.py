import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf(filename, title, sections):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0D47A1'),
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'Heading2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1565C0'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#212121'),
        spaceAfter=8
    )

    story = [
        Paragraph(title, title_style),
        Paragraph("<b>Official Government Citizen Reference Manual</b>", styles['Italic']),
        Spacer(1, 14)
    ]
    
    for sec_heading, sec_paragraphs in sections:
        story.append(Paragraph(sec_heading, h2_style))
        for p in sec_paragraphs:
            story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 8))
        
    doc.build(story)
    print(f"Generated PDF: {filename}")

if __name__ == "__main__":
    # 1. Post Office PDF
    po_sections = [
        ("1. Speed Post Domestic Guidelines", [
            "Speed Post is the flagship premium postal courier service provided by the Department of Posts, Government of India. It offers guaranteed delivery throughout India.",
            "Weight limit for Speed Post parcels is up to 35 kilograms. Local deliveries are made within 1 to 2 working days, metro-to-metro in 1 to 3 days, and rest of India in 2 to 5 days.",
            "Each parcel booked via Speed Post receives a unique 13-character tracking number (e.g., SP123456789IN). Parcels can be tracked online at indiapost.gov.in or via SMS by texting 'POST TRACK &lt;13-digit-ID&gt;' to 166 or 51969."
        ]),
        ("2. Domestic Parcel Booking and Packaging", [
            "For non-urgent heavy consignments up to 20 kilograms, citizens can choose Registered Parcel services.",
            "All parcels must be securely packaged in sturdy cardboard or cloth wrapped and stitched. Prohibited items include flammable substances, explosives, currency notes, and hazardous liquids.",
            "For inter-state commercial consignments, appropriate GST invoices or declarations must accompany the package. Senders must legibly mention recipient and sender complete address with 6-digit postal PIN code."
        ]),
        ("3. Post Office Savings Schemes & IPPB", [
            "Post Office Savings Bank (POSB) accounts can be opened with an initial deposit of Rs. 500. Individual accounts earn 4.0% interest per annum. Nomination is mandatory.",
            "India Post Payments Bank (IPPB) offers 100% digital, zero-balance doorstep banking. Gramin Dak Sevaks and postmen visit citizen homes equipped with biometric micro-ATM devices. Only Aadhaar and registered mobile are required for instant 5-minute account opening."
        ])
    ]
    create_pdf("data/documents/post_office/Speed_Post_and_Parcel_Guidelines.pdf", "India Post - Speed Post & Citizen Services Manual", po_sections)

    # 2. Banking PDF
    bank_sections = [
        ("1. Bank Account Opening & KYC Norms", [
            "Under the Reserve Bank of India (RBI) Master Directions, banks require Officially Valid Documents (OVD) for Know Your Customer (KYC) verification. OVDs include Passport, Driving License, Voter ID Card, Aadhaar Card, NREGA Job Card, and NPR Letter.",
            "Permanent Account Number (PAN) or Form 60 is mandatory for all savings accounts.",
            "Basic Savings Bank Deposit Accounts (BSBDA) / PMJDY accounts require zero minimum balance and offer 4 free withdrawals monthly without maintenance penalties.",
            "Video KYC (V-CIP) permits seamless digital account opening from home via live smartphone audio-visual verification with bank officials."
        ]),
        ("2. UPI Payments and Anti-Fraud Security Protocols", [
            "Unified Payments Interface (UPI) developed by NPCI allows 24x7 instant fund transfers between bank accounts.",
            "CRITICAL FRAUD WARNING: Entering your secret UPI PIN is ONLY needed to SEND money, NEVER to receive funds. Any request to enter a UPI PIN or scan a QR code to claim cashbacks, prizes, or receive money is fraudulent.",
            "Never download screen-sharing utilities (AnyDesk, TeamViewer, RustDesk) at the request of unverified callers.",
            "If an unauthorized transaction occurs, immediately report to the National Cyber Crime Helpline at 1930 or on cybercrime.gov.in."
        ]),
        ("3. RBI Integrated Ombudsman Scheme", [
            "If a customer complaint is not resolved satisfactorily by the bank within 30 days, customers can file a grievance free of cost with the RBI Integrated Ombudsman at cms.rbi.org.in or helpline 14448."
        ])
    ]
    create_pdf("data/documents/banking/RBI_KYC_and_Account_Opening_Handbook.pdf", "Reserve Bank of India - KYC & Digital Banking Guidelines", bank_sections)

    # 3. Transportation PDF
    trans_sections = [
        ("1. Indian Railways Ticket Booking & Tatkal Rules", [
            "Advance railway reservations can be booked 120 days in advance on www.irctc.co.in or IRCTC Rail Connect mobile application.",
            "Tatkal Booking Windows: AC classes (1A, 2A, 3A, CC, 3E) open at 10:00 AM IST one day prior to train departure from originating station. Non-AC classes (Sleeper, 2S) open at 11:00 AM IST.",
            "Maximum 4 passengers per Tatkal PNR. Confirmed Tatkal tickets are non-refundable upon cancellation, except in specific delay situations.",
            "Passengers must carry at least one original valid government identity card during travel (Aadhaar, Voter ID, Passport, PAN Card, Driving License)."
        ]),
        ("2. Concessional State Bus Passes & NCMC", [
            "State Road Transport Corporations (TSRTC, APSRTC, DTC, BMTC, MSRTC) offer concessional travel passes for students and senior citizens (aged 60 and above).",
            "Student passes require an educational bonafide certificate, photographs, and institutional attestation.",
            "The National Common Mobility Card (NCMC) is an interoperable RuPay card usable across metro transit, state buses, tolls, and parking throughout India."
        ])
    ]
    create_pdf("data/documents/transportation/Indian_Railways_Reservation_Rules.pdf", "Ministry of Railways & Public Transit Guidelines", trans_sections)

    # 4. Government Services PDF
    gov_sections = [
        ("1. State Citizen Certificates (ServicePlus & State Portals)", [
            "Citizens can apply online for Income, Caste/Community, and Domicile/Residence certificates via state portals (MeeSeva, e-District, Nadakacheri, Aaple Sarkar) or ServicePlus (serviceonline.gov.in).",
            "Income Certificates: Required for welfare subsidies and educational scholarships. Valid for one financial year. Requires salary slips, income tax documents, or self-declaration affidavit.",
            "Community / Caste Certificates: Issued by the Revenue Department (Tahsildar / SDM) establishing SC/ST/OBC status. SC/ST certificates are permanent; OBC Non-Creamy Layer certificates require annual renewal.",
            "Approved certificates are issued with verifiable QR codes and digital signatures within 7 to 15 working days."
        ]),
        ("2. DigiLocker Legal Framework & Document Issuance", [
            "DigiLocker is the Government of India flagship cloud wallet under Digital India.",
            "Under Rule 9A of the IT Rules 2016, electronic records in DigiLocker issued by authorities are treated at par with original physical documents.",
            "Citizens can fetch digitally signed Aadhaar, Driving License, Vehicle RC, and educational marksheets directly from official repositories using Aadhaar authentication."
        ])
    ]
    create_pdf("data/documents/government/Citizen_Certificates_and_DigiLocker_Manual.pdf", "Government Citizen Certificates & DigiLocker Handbook", gov_sections)

