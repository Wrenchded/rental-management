from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import shutil
from database import init_db, get_db_connection, generate_unique_id
from typing import List, Optional
from datetime import datetime
import random
import traceback
import sqlite3


app = FastAPI()

# 🛡️ Layer 1: Session Middleware Initialization Node
app.add_middleware(SessionMiddleware, secret_key="YOUR_SECURE_PORTAL_APP_KEY_SECRET_TOKEN")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Guarantee database structure initialization layer runs on startup
init_db()

# =====================================================================
# 📂 CENTRAL WEB APPLICATION TRANSLATION DICTIONARY MATRIX
# =====================================================================
TRANSLATIONS = {
    "en": {
        "app_title": "OUR COMPANY LOGO & NAME",
        "portal_sub": "RESIDENT PORTAL HUB",
        "tenant_reg": "Tenant Registration",
        "induction_profile": "Onboard Tenant Induction Profile",
        "support_desk": "Support Desk",
        "issue_tracking": "File Issue Tracking Parameters",
        "full_name": "Full Name",
        "fathers_name": "Father's Name",
        "mothers_name": "Mother's Name",
        "aadhaar_label": "Identity Verification Document",
        "allocation_label": "Select Bed/Room Allocation",
        "work_college_label": "Present Work / College Name",
        "permanent_address": "Permanent Address",
        "current_address": "Current Address",
        "negotiated_rent": "Negotiated Rent Allocation (₹ / Month)",
        "rent_matrix_hint": "Overrides default asset pricing matrices individually per contract.",
        "submit_profile_btn": "Complete Account Profile",
        "sign_out": "Sign Out Current Profile Session",
        "issue_category": "Issue Category",
        "detailed_desc": "Detailed Description",
        "dispatch_ticket_btn": "Dispatch Maintenance Ticket",
        "notice_label": "Notice:",
        "notice_body": "This issue log is dispatched directly onto your manager's primary dashboard control room for logging resolution pipelines.",
        "support_router_active": "Support Node Router Active",
        "my_profile": "My Profile",
        "rent_due": "Rent Due",
        "receipts": "Receipts",
        "room_info": "Room Info",
        "attendance": "Attendance",
        "notices": "Notices",
        "agreement": "Agreement",
        "gate_pass": "Gate Pass",
        "complaints": "Complaints",
        "home_info": "Home Info",
        "wifi_access": "WiFi Access",
        "emergency": "Emergency",
        "advertise_window": "ADVERTISE WINDOW"
    },
    "hi": {
        "app_title": "हमारी कंपनी का लोगो और नाम",
        "portal_sub": "निवासी पोर्टल हब",
        "tenant_reg": "किराएदार पंजीकरण",
        "induction_profile": "किराएदार प्रेरण प्रोफ़ाइल",
        "support_desk": "सहायता केंद्र",
        "issue_tracking": "समस्या ट्रैकिंग मापदंड दर्ज करें",
        "full_name": "पूरा नाम",
        "fathers_name": "पिता का नाम",
        "mothers_name": "माता का नाम",
        "aadhaar_label": "पहचान सत्यापन दस्तावेज़",
        "allocation_label": "बेड/कमरा आवंटन चुनें",
        "work_college_label": "वर्तमान कार्य / कॉलेज का नाम",
        "permanent_address": "स्थायी पता",
        "current_address": "वर्तमान पता",
        "negotiated_rent": "परेशान किराया आवंटन (₹ / महीना)",
        "rent_matrix_hint": "प्रति अनुबंध व्यक्तिगत रूप से डिफ़ॉल्ट संपत्ति मूल्य निर्धारण मेट्रिक्स को ओवरराइड करता है।",
        "submit_profile_btn": "खाता प्रोफ़ाइल पूरा करें",
        "sign_out": "वर्तमान प्रोफ़ाइल सत्र साइन आउट करें",
        "issue_category": "समस्या की श्रेणी",
        "detailed_desc": "विस्तृत विवरण",
        "dispatch_ticket_btn": "रखरखाव टिकट भेजें",
        "notice_label": "सूचना:",
        "notice_body": "यह समस्या लॉग रिज़ॉल्यूशन पाइपलाइनों के लिए सीधे आपके प्रबंधक के प्राथमिक डैशबोर्ड नियंत्रण कक्ष में भेजा जाता है।",
        "support_router_active": "सहायता नोड राउटर सक्रिय",
        "my_profile": "मेरी प्रोफ़ाइल",
        "rent_due": "किराया बकाया",
        "receipts": "रसीदें",
        "room_info": "कमरे की जानकारी",
        "attendance": "उपस्थिति",
        "notices": "नोटिस",
        "agreement": "अनुबंध पत्र",
        "gate_pass": "गेट पास",
        "complaints": "शिकायतें",
        "home_info": "घर की जानकारी",
        "wifi_access": "वाईफाई एक्सेस",
        "emergency": "आपातकालीन",
        "advertise_window": "विज्ञापन विंडो"
    },
    "mr": {
        "app_title": "आमच्या कंपनीचा लोगो आणि नाव",
        "portal_sub": "निवासी पोर्टल हब",
        "tenant_reg": "भाडेकरू नोंदणी",
        "induction_profile": "भाडेकरू इंडक्शन प्रोफाइल",
        "support_desk": "मदत केंद्र",
        "issue_tracking": "तक्रार ट्रॅकिंग पॅरामीटर्स",
        "full_name": "पूर्ण नाव",
        "fathers_name": "वडिलांचे नाव",
        "mothers_name": "आहेचे नाव",
        "aadhaar_label": "ओळख पडताळणी दस्तऐवज",
        "allocation_label": "बेड/खोली वाटप निवडा",
        "work_college_label": "सध्याचे काम / कॉलेजचे नाव",
        "permanent_address": "कायमचा पत्ता",
        "current_address": "सध्याचा पत्ता",
        "negotiated_rent": "वाटाघाटी केलेले भाडे वाटप (₹ / महिना)",
        "rent_matrix_hint": "प्रत्येक कराराच्या आधारावर डीफॉल्ट मालमत्ता किंमत मॅट्रिक्स ओव्हरराइड करते.",
        "submit_profile_btn": "खाते प्रोफाइल पूर्ण करा",
        "sign_out": "सध्याचे प्रोफाइल सत्र साइन आउट करा",
        "issue_category": "तक्रारीची श्रेणी",
        "detailed_desc": "सविस्तर वर्णन",
        "dispatch_ticket_btn": "देखभाल तिकीट पाठवा",
        "notice_label": "सूचना:",
        "notice_body": "हा तक्रार लॉग रिझोल्यूशन पाइपलाइनसाठी थेट तुमच्या व्यवस्थापकाच्या प्राथमिक डॅशबोर्ड नियंत्रण कक्षाकडे पाठवला जातो.",
        "support_node_active": "सपोर्ट नोड सक्रिय",
        "my_profile": "माझी प्रोफाइल",
        "rent_due": "भाडे देय",
        "receipts": "पावत्या",
        "room_info": "खोलीची माहिती",
        "attendance": "हजेरी",
        "notices": "नोटीस",
        "agreement": "करारनामा",
        "gate_pass": "गेट पास",
        "complaints": "तक्रारी",
        "home_info": "घराची माहिती",
        "wifi_access": "वायफाय ऍक्सेस",
        "emergency": "आणीबाणी",
        "advertise_window": "जाहिरात विंडो"
    }
}

# 🧠 Layer 2: Translation Engine Middleware Interceptor Dependency
def get_translator(request: Request):
    lang = request.session.get("lang", "en")
    def translate(key: str) -> str:
        return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    return translate


# =====================================================================
# 🌐 GLOBAL LANG ROUTE CONTROLLER
# =====================================================================
@app.get("/set-language/{lang}")
async def dynamic_set_app_language(lang: str, request: Request):
    if lang in ["en", "hi", "mr"]:
        request.session["lang"] = lang
    referer = request.headers.get("referer", "/")
    return RedirectResponse(url=referer)


# 1. ENTRY VIEW PORTAL GATEWAY
@app.get("/", response_class=HTMLResponse)
async def serve_entry_screen(request: Request, _=Depends(get_translator)):
    return templates.TemplateResponse(request=request, name="entry.html", context={"_": _})

# 2. DISCOVERY ROUTER SWITCH GATEWAY
@app.post("/login")
async def handle_login(request: Request, mobile: str = Form(...), email: str = Form(...), role: str = Form(...), _=Depends(get_translator)):
    conn = get_db_connection()
    if role == "Owner":
        user = conn.execute("SELECT owner_id FROM Owners WHERE mobile=? OR email=?", (mobile, email)).fetchone()
        conn.close()
        if user:
            return RedirectResponse(url=f"/dashboard/owner/{user['owner_id']}", status_code=303)
        else:
            return templates.TemplateResponse(request=request, name="owner_reg.html", context={"mobile": mobile, "email": email, "_": _})
    else:
        user = conn.execute("SELECT tenant_id FROM Tenants WHERE mobile=? OR email=?", (mobile, email)).fetchone()
        active_property = conn.execute("SELECT owner_id, property_type FROM Properties ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        
        if user:
            return RedirectResponse(url=f"/dashboard/tenant/{user['tenant_id']}", status_code=303)
        else:
            target_owner = active_property["owner_id"] if active_property else "OWN-000001"
            target_type = active_property["property_type"] if active_property else "PG"
            
            return templates.TemplateResponse(
                request=request, 
                name="tenant_reg.html", 
                context={
                    "mobile": mobile, 
                    "email": email,
                    "owner_id": target_owner,
                    "property_type": target_type,
                    "_": _
                }
            )

# 3. OWNER PROFILE DATA COLLECTOR PIPELINE
@app.post("/register/owner")
async def register_owner(request: Request, 
                         name: str = Form(...), 
                         mobile: str = Form(...), 
                         email: str = Form(...), 
                         aadhaar: str = Form(...), 
                         property_types: List[str] = Form([]), 
                         property_address: str = Form(...), 
                         photo: UploadFile = File(None),
                         _=Depends(get_translator)):
    new_id = generate_unique_id("OWN")
    photo_path = ""
    
    if photo and photo.filename:
        photo_path = f"uploads/profile_photos/{new_id}.png"
        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
            
    joined_types = ", ".join(property_types) if property_types else "N/A"
    primary_type = property_types[0] if property_types else "PG"
            
    conn = get_db_connection()
    conn.execute("INSERT INTO Owners (owner_id, name, mobile, email, aadhaar, property_type, property_address, profile_photo) VALUES (?,?,?,?,?,?,?,?)",
                 (new_id, name, mobile, email, "[Aadhaar Redacted]", joined_types, property_address, photo_path))
    conn.commit()
    conn.close()
    
    return templates.TemplateResponse(request=request, name="property_config.html", context={
        "owner_id": new_id,
        "default_type": primary_type,
        "_": _
    })

# 4. DEPRECATED ROUTE
@app.post("/register/property")
async def register_property(owner_id: str = Form(...), pg_name: str = Form(...), corporation_name: str = Form(...),
                            total_rooms: int = Form(...), total_beds: int = Form(...), occupied_beds: int = Form(...),
                            address: str = Form(...)):
    avail_beds = total_beds - occupied_beds
    conn = get_db_connection()
    conn.execute("INSERT INTO Properties (owner_id, pg_name, corporation_name, total_rooms, total_beds, occupied_beds, available_beds, address) VALUES (?,?,?,?,?,?,?,?)",
                 (owner_id, pg_name, corporation_name, total_rooms, total_beds, occupied_beds, avail_beds, address))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/dashboard/owner/{owner_id}", status_code=303)

# 5. REFACTORED TENANT PROFILE SUBMISSION PIPELINE (UPDATED WITH DYNAMIC ASSET TYPE CHECK)
@app.post("/tenant/register")
@app.post("/register/tenant")
async def register_tenant(request: Request, 
                          tenant_name: str = Form(...), 
                          tenant_contact: str = Form(...), 
                          emergency_contact: str = Form(...),
                          email: str = Form(...), 
                          identity_document_type: str = Form(...), 
                          id_number: str = Form(...), 
                          property_card_number: str = Form(...),
                          vehicle_type: str = Form(...),
                          vehicle_number: Optional[str] = Form(None),
                          advance_amount: float = Form(...),
                          stay_start_date: str = Form(...),
                          owner_id: str = Form(...),
                          institution_name: Optional[str] = Form(None),
                          identity_file: Optional[UploadFile] = File(None)):
    
    new_id = generate_unique_id("TEN")
    secure_id_number = "[Identity Document Redacted]" if identity_document_type == "Aadhaar" else id_number
    clean_vehicle_number = vehicle_number if vehicle_type != "None" else ""
    
    saved_file_path = ""
    if identity_file and identity_file.filename:
        upload_dir = os.path.join(BASE_DIR, "uploads", "identity_documents")
        os.makedirs(upload_dir, exist_ok=True)
        
        _, ext = os.path.splitext(identity_file.filename)
        filename = f"{new_id}_document{ext}"
        saved_file_path = os.path.join("uploads", "identity_documents", filename)
        
        full_dest_path = os.path.join(BASE_DIR, saved_file_path)
        with open(full_dest_path, "wb") as buffer:
            shutil.copyfileobj(identity_file.file, buffer)
    
    COMMISSION_RATE = 0.10
    platform_commission = advance_amount * COMMISSION_RATE
    owner_earnings = advance_amount - platform_commission
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Insert into Tenants Table
    cursor.execute("""
        INSERT INTO Tenants (
            tenant_id, owner_id, name, mobile, emergency_contact, tenant_contact, email, 
            identity_document_type, id_number, document_file_path, allocated_unit, vehicle_type, 
            vehicle_number, advance_amount, stay_start_date, allocated_rent, institution
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (new_id, owner_id, tenant_name, tenant_contact, emergency_contact, tenant_contact, email, 
          identity_document_type, secure_id_number, saved_file_path if saved_file_path else "N/A", 
          property_card_number, vehicle_type, clean_vehicle_number, advance_amount, stay_start_date, 
          advance_amount, institution_name if institution_name else "N/A")) 
    
    # ⚙️ 2. Dynamic Asset Occupancy Counters Update Layer (Fixes the -2/0 Beds Bug)
    cursor.execute("SELECT property_type FROM Properties WHERE owner_id = ?", (owner_id,))
    target_property = cursor.fetchone()
    
    if target_property and target_property["property_type"] == "PG":
        # PG: Beds are incremented individually per reservation
        cursor.execute("""
            UPDATE Properties 
            SET occupied_beds = occupied_beds + 1,
                available_beds = available_beds - 1
            WHERE owner_id = ?
        """, (owner_id,))
    else:
        # Flat, Office, Commercial, Chawl, Godown, Shed, Open Space: Full unit becomes leased
        cursor.execute("""
            UPDATE Properties 
            SET total_rooms = 1,
                occupied_beds = 1,
                available_beds = 0
            WHERE owner_id = ?
        """, (owner_id,))
    
    # 3. Log the Registration Payment into the Transactions Ledger
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(6)])
    txn_id = f"TXN-{random_digits}"
    
    cursor.execute("""
        INSERT INTO Transactions (
            transaction_id, owner_id, tenant_id, agreement_id, 
            payment_type, total_collected, platform_commission, 
            owner_earnings, payment_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (txn_id, owner_id, new_id, "AGR-FIRST-CYCLE", 
          "Rent", advance_amount, platform_commission, owner_earnings, "Paid"))
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(url=f"/dashboard/tenant/{new_id}", status_code=303)

# 6. OWNER DASHBOARD
# 6. OWNER DASHBOARD
@app.get("/dashboard/owner/{owner_id}", response_class=HTMLResponse)
async def view_owner_dashboard(request: Request, owner_id: str, _=Depends(get_translator)):
    conn = get_db_connection()

    # IMPORTANT: row factory BEFORE queries
    conn.row_factory = sqlite3.Row

    owner_row = conn.execute(
        "SELECT * FROM Owners WHERE owner_id=?",
        (owner_id,)
    ).fetchone()

    prop_row = conn.execute(
        "SELECT * FROM Properties WHERE owner_id=?",
        (owner_id,)
    ).fetchone()

    tenants = conn.execute(
        "SELECT allocated_rent FROM Tenants WHERE owner_id=?",
        (owner_id,)
    ).fetchall()

    calculated_yield = sum([t["allocated_rent"] for t in tenants]) if tenants else 0.0

    all_tickets = conn.execute("""
        SELECT t.name as tenant_name, m.ticket_id, m.category, m.description, m.status 
        FROM MaintenanceTickets m
        JOIN Tenants t ON m.tenant_id = t.tenant_id
        WHERE m.owner_id = ? 
        ORDER BY m.id DESC
    """, (owner_id,)).fetchall()

    conn.close()

    # ---------------- OWNER CONTEXT ----------------
    owner_context = dict(owner_row) if owner_row else None

    # ---------------- PROP CONTEXT (UPDATED WITH PREMIUM CONDITIONAL SAFETY) ----------------
    if prop_row:
        property_type = prop_row["property_type"]
        total_rooms = prop_row["total_rooms"]
        total_beds = prop_row["total_beds"]
        occupied_beds = prop_row["occupied_beds"]
        available_beds = prop_row["available_beds"]

        # ✅ FIX 3: Premium UI formatting safety layer implementation
        raw_bhk = prop_row["flat_bhk"]
        if raw_bhk:
            # Cleans inputs dynamically (e.g., converts '3' or '3bhk' cleanly into '3 BHK')
            cleaned_bhk = str(raw_bhk).upper().replace("BHK", "").strip()
            flat_bhk_display = f"{cleaned_bhk} BHK"
        else:
            flat_bhk_display = "Not Specified"

        prop_context = {
            # core identity
            "property_type": property_type or "Not Set",

            # capacity mapping (NEW UI FRIENDLY FIELDS)
            "total_capacity": total_beds if total_beds else total_rooms,
            "leased": occupied_beds if occupied_beds else 0,
            "available": available_beds if available_beds else 0,

            # raw DB values (keep for backend use)
            "total_rooms": total_rooms,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,

            # type-specific (CLEAN VALUE ASSIGNMENTS)
            "flat_bhk": flat_bhk_display,
            "office_cabins": prop_row["office_cabins"] or 0,
            "office_workstations": prop_row["office_workstations"] or 0,
            "chawl_room_number": prop_row["chawl_room_number"],
            "chawl_unit_number": prop_row["chawl_unit_number"],
            "generic_area_specification": prop_row["generic_area_specification"]
        }
    else:
        # Fallback dictionary if no property record exists in the database
        prop_context = {
            "property_type": "Not Set",
            "total_capacity": 0,
            "leased": 0,
            "available": 0,
            "total_rooms": 0,
            "total_beds": 0,
            "occupied_beds": 0,
            "available_beds": 0,
            "flat_bhk": "Unconfigured",
            "office_cabins": 0,
            "office_workstations": 0,
            "chawl_room_number": None
        }

    # ---------------- TICKET SPLIT ----------------
    active_tickets = [t for t in all_tickets if t["status"] == "Open"]
    history_tickets = [t for t in all_tickets if t["status"] == "Resolved"]

    return templates.TemplateResponse(
        request=request,
        name="owner_dash.html",
        context={
            "owner": owner_context,
            "prop": prop_context,
            "calculated_yield": f"{calculated_yield:,.2f}",
            "tickets": active_tickets,
            "history_tickets": history_tickets,
            "ticket_count": len(active_tickets),
            "_": _
        }
    )

@app.post("/dashboard/owner/resolve-ticket")
async def resolve_maintenance_ticket(owner_id: str = Form(...), ticket_id: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE MaintenanceTickets 
        SET status = 'Resolved' 
        WHERE ticket_id = ? AND owner_id = ?
    """, (ticket_id, owner_id))
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(url=f"/dashboard/owner/{owner_id}", status_code=303)

# 7. TENANT DASHBOARD
@app.get("/dashboard/tenant/{tenant_id}", response_class=HTMLResponse)
async def serve_tenant_dashboard(request: Request, tenant_id: str, _=Depends(get_translator)):
    conn = get_db_connection()
    tenant = conn.execute("SELECT * FROM Tenants WHERE tenant_id=?", (tenant_id,)).fetchone()
    conn.close()
    
    return templates.TemplateResponse(request=request, name="tenant_dash.html", context={"tenant": tenant, "_": _})

# 📜 ROUTE: Dynamic Digital Legal Agreement Compilation Engine
@app.get("/dashboard/tenant/{tenant_id}/agreement", response_class=HTMLResponse)
async def generate_digital_agreement(request: Request, tenant_id: str, _=Depends(get_translator)):
    conn = get_db_connection()
    tenant = conn.execute("SELECT * FROM Tenants WHERE tenant_id=?", (tenant_id,)).fetchone()
    
    if not tenant:
        conn.close()
        raise HTTPException(status_code=404, detail="Tenant profile record not found in system storage node.")
    
    associated_owner_id = tenant["owner_id"]
    owner = conn.execute("SELECT * FROM Owners WHERE owner_id=?", (associated_owner_id,)).fetchone()
    prop = conn.execute("SELECT * FROM Properties WHERE owner_id=?", (associated_owner_id,)).fetchone()
    
    txn = conn.execute("SELECT platform_commission, owner_earnings FROM Transactions WHERE tenant_id=?", (tenant_id,)).fetchone()
    
    conn.close()

    today = datetime.now().strftime("%dth %B, %Y")
    
    return templates.TemplateResponse(
        request=request,
        name="agreement_template.html",
        context={
            "tenant": tenant,
            "owner": owner,
            "prop": prop,
            "agreement_date": today,
            "platform_commission": txn['platform_commission'] if txn else 0,
            "owner_earnings": txn['owner_earnings'] if txn else 0,
            "_": _
        }
    )

# 🛠️ GET Route to Render the Tenant Maintenance Form Node
@app.get("/dashboard/tenant/{tenant_id}/complaints", response_class=HTMLResponse)
async def view_complaint_form(request: Request, tenant_id: str, _=Depends(get_translator)):
    conn = get_db_connection()
    tenant = conn.execute("SELECT * FROM Tenants WHERE tenant_id=?", (tenant_id,)).fetchone()
    conn.close()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant registry footprint not found.")
        
    return templates.TemplateResponse(
        request=request, 
        name="complaint_form.html", 
        context={
            "tenant": tenant,
            "tenant_id": tenant_id,
            "_": _
        }
    )

@app.get("/dashboard/add-technician", response_class=HTMLResponse)
async def add_technician_page(request: Request):
    return templates.TemplateResponse("add_technician.html", {"request": request})

@app.get("/dashboard/add-technician/{owner_id}", response_class=HTMLResponse)
async def add_technician_page(request: Request, owner_id: str):
    conn = get_db_connection()
    owner = conn.execute("SELECT * FROM Owners WHERE owner_id = ?", (owner_id,)).fetchone()
    conn.close()
    
    return templates.TemplateResponse(
        request=request, 
        name="add_technician.html", 
        context={"owner": owner}
    )

@app.post("/dashboard/add-technician")
async def process_new_technician(
    owner_id: str = Form(...),
    name: str = Form(...),
    specialization: str = Form(...),
    phone: str = Form(...) 
):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Technicians (name, specialization, contact_number, owner_id) VALUES (?, ?, ?, ?)",
        (name, specialization, phone, owner_id)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/dashboard/owner/{owner_id}", status_code=303)

# 🛠️ NEW: Route to View Ticket Details & Assign Technician
@app.get("/dashboard/owner/ticket/{ticket_id}", response_class=HTMLResponse)
async def view_ticket_details(request: Request, ticket_id: str, _=Depends(get_translator)):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM MaintenanceTickets WHERE ticket_id=?", (ticket_id,)).fetchone()
    technicians = conn.execute("SELECT * FROM Technicians").fetchall()
    conn.close()
    
    return templates.TemplateResponse(
        request=request, 
        name="view_ticket.html", 
        context={
            "ticket": ticket,
            "technicians": technicians,
            "_": _
        }
    )

# 🛠️ NEW: Route to Handle Assignment
@app.post("/dashboard/owner/assign-technician/{ticket_id}")
async def assign_technician(ticket_id: str, owner_id: str = Form(...), technician_id: int = Form(...)):
    conn = get_db_connection()
    conn.execute(
        "UPDATE MaintenanceTickets SET technician_id = ? WHERE ticket_id = ?",
        (technician_id, ticket_id)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/dashboard/owner/{owner_id}", status_code=303)

@app.post("/dashboard/owner/resolve-ticket-and-bill/{ticket_id}")
async def resolve_and_bill(
    ticket_id: str, 
    owner_id: str = Form(...), 
    tech_id: int = Form(...),
    hours_spent: float = Form(...), 
    parts_cost: float = Form(...),
    parts_description: str = Form(...)
):
    labor_rate = 200 
    total_amount = (hours_spent * labor_rate) + parts_cost
    
    conn = get_db_connection()
    conn.execute("UPDATE MaintenanceTickets SET status = 'Resolved' WHERE ticket_id = ?", (ticket_id,))
    
    conn.execute("""
        INSERT INTO ServiceLogs 
        (complaint_id, tech_id, hours_spent, parts_cost, parts_description, total_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ticket_id, tech_id, hours_spent, parts_cost, parts_description, total_amount))
    
    conn.commit()
    conn.close()

    print("REDIRECTING TO:", f"/dashboard/owner/invoice/{ticket_id}")
    
    return RedirectResponse(url=f"/dashboard/owner/invoice/{ticket_id}", status_code=303)

@app.get("/dashboard/owner/invoice/{ticket_id}")
async def view_invoice(request: Request, ticket_id: str):
    conn = get_db_connection()

    try:
        log_row = conn.execute(
            "SELECT * FROM ServiceLogs WHERE complaint_id = ?",
            (ticket_id,)
        ).fetchone()

        ticket_row = conn.execute(
            "SELECT * FROM MaintenanceTickets WHERE ticket_id = ?",
            (ticket_id,)
        ).fetchone()

        tech_row = None
        if log_row:
            tech_row = conn.execute(
                "SELECT * FROM Technicians WHERE tech_id = ?",
                (log_row["tech_id"],)
            ).fetchone()

        tenant_row = None
        if ticket_row:
            tenant_id = ticket_row["tenant_id"]
            tenant_row = conn.execute(
                "SELECT * FROM Tenants WHERE tenant_id = ?",
                (tenant_id,)
            ).fetchone()

        if not log_row or not ticket_row or not tenant_row or not tech_row:
            return HTMLResponse("<h1>Error: Could not retrieve invoice data.</h1>")

        data = {
            "complaint_id": log_row["complaint_id"],
            "service_date": log_row["service_date"],
            "hours_spent": log_row["hours_spent"],
            "parts_cost": log_row["parts_cost"],
            "parts_description": str(log_row["parts_description"]),
            "total_amount": log_row["total_amount"],
            "tenant_name": tenant_row["name"],
            "allocated_unit": tenant_row["allocated_unit"],
            "labor_cost": log_row["hours_spent"] * 200,
            "tech_name": tech_row["name"],
            "specialization": tech_row["specialization"]
        }

        return templates.TemplateResponse(
            request=request,
            name="invoice_template.html",
            context={
                "log": log_row,
                "tenant": tenant_row,
                "technician": tech_row,
                "labor_cost": log_row["hours_spent"] * 200,
                "data": data,
                "owner_id": ticket_row["owner_id"]
            }
        )

    except Exception as e:
        return HTMLResponse(f"<pre>{traceback.format_exc()}</pre>")

    finally:
        conn.close()
        
@app.get("/dashboard/owner/service-history", response_class=HTMLResponse)
async def view_service_history(request: Request, _=Depends(get_translator)):
    conn = get_db_connection()
    history = conn.execute("""
        SELECT s.*, t.name, mt.category 
        FROM ServiceLogs s 
        JOIN Technicians t ON s.tech_id = t.tech_id
        JOIN MaintenanceTickets mt ON s.complaint_id = mt.ticket_id
    """).fetchall()
    conn.close()
    
    return templates.TemplateResponse("service_history.html", {"request": request, "history": history})

# 🛠️ POST Route to Catch, Process, and Commit the Ticket Entry
@app.post("/dashboard/tenant/{tenant_id}/complaints")
async def dispatch_maintenance_ticket(tenant_id: str, 
                                      owner_id: str = Form(...), 
                                      category: str = Form(...), 
                                      description: str = Form(...)):
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    ticket_id = f"TKT-{random_digits}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO MaintenanceTickets (ticket_id, tenant_id, owner_id, category, description)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket_id, tenant_id, owner_id, category, description))
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(url=f"/dashboard/tenant/{tenant_id}", status_code=303)

# 🏢 ROUTE 1: Serve the Property Configuration Screen
@app.get("/property/configure/{owner_id}")
async def view_property_config(request: Request, owner_id: str, _=Depends(get_translator)):
    return templates.TemplateResponse(
        request=request, 
        name="property_config.html", 
        context={
            "owner_id": owner_id,
            "default_type": "PG",
            "_": _
        }
    )


# 🚀 ROUTE 2: Process the Configuration Form and Save/Update DB
@app.post("/property/configure/{owner_id}")
async def process_property_config(
    request: Request,
    owner_id: str,
    property_card_number: str = Form(...),
    pg_name: str = Form(...),
    property_type: str = Form(...),
    total_rooms: int = Form(0),
    total_beds: int = Form(0),
    flat_bhk: Optional[str] = Form(None),
    flat_furnishing: Optional[str] = Form(None),
    flat_ac_status: Optional[str] = Form(None),
    flat_parking: Optional[str] = Form(None),
    flat_security: Optional[str] = Form(None),
    office_cabins: int = Form(0),
    office_workstations: int = Form(0),
    office_meeting_rooms: int = Form(0),
    office_reception_status: Optional[str] = Form(None),
    office_internet_facility: Optional[str] = Form(None),
    office_parking_status: Optional[str] = Form(None),
    chawl_room_number: Optional[str] = Form(None),
    chawl_unit_number: Optional[str] = Form(None),
    chawl_water_connection: Optional[str] = Form(None),
    chawl_electricity_meter_no: Optional[str] = Form(None),
    generic_area_specification: Optional[str] = Form(None),
    facilities: List[str] = Form(None),
    property_terms: Optional[str] = Form(None),
    _=Depends(get_translator)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure property record exists
    cursor.execute("SELECT 1 FROM Properties WHERE owner_id = ?", (owner_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO Properties (owner_id) VALUES (?)", (owner_id,))

    # Asset Classification Normalization
    if property_type == "Flat":
        total_rooms = 0
        total_beds = 0
    elif property_type == "PG":
        flat_bhk = None
        office_cabins = 0
        office_workstations = 0
    elif property_type == "Office":
        total_beds = 0
        flat_bhk = None
    elif property_type == "Chawl":
        total_beds = 0
        flat_bhk = None
        office_cabins = 0
        office_workstations = 0

    cursor.execute("""
        UPDATE Properties 
        SET property_type = ?, 
            property_card_no = ?, 
            property_card_number = ?, 
            pg_name = ?, 
            total_rooms = ?, 
            total_beds = ?, 
            available_beds = ?,
            flat_bhk = ?,
            flat_furnishing = ?,
            flat_ac_status = ?,
            flat_parking = ?,
            flat_security = ?,
            office_cabins = ?,
            office_workstations = ?,
            office_meeting_rooms = ?,
            office_reception_status = ?,
            office_internet_facility = ?,
            office_parking_status = ?,
            chawl_room_number = ?,
            chawl_unit_number = ?,
            chawl_water_connection = ?,
            chawl_electricity_meter_no = ?,
            generic_area_specification = ?,
            property_terms = ?
        WHERE owner_id = ?
    """, (
        property_type, property_card_number, property_card_number, pg_name,
        total_rooms, total_beds, total_beds,
        flat_bhk, flat_furnishing, flat_ac_status, flat_parking, flat_security,
        office_cabins, office_workstations, office_meeting_rooms,
        office_reception_status, office_internet_facility, office_parking_status,
        chawl_room_number, chawl_unit_number, chawl_water_connection, chawl_electricity_meter_no,
        generic_area_specification,
        property_terms if property_terms else "",
        owner_id
    ))

    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/dashboard/owner/{owner_id}", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)