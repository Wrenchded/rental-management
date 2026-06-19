import sqlite3
import os

DB_PATH = "rental_management.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Ensure system upload directories exist cleanly
    os.makedirs("uploads/profile_photos", exist_ok=True)
    os.makedirs("uploads/identity_documents", exist_ok=True)
    os.makedirs("uploads/signatures", exist_ok=True)
    os.makedirs("uploads/agreements", exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. ADMIN SYSTEM SETTINGS TABLE (Requirement 11 & 12)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AdminSettings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            commission_type TEXT DEFAULT 'Percentage', -- 'Fixed' or 'Percentage'
            commission_value REAL DEFAULT 10.0,         -- e.g., 100 Rs or 10%
            subscription_monthly_rate REAL DEFAULT 499.0,
            advertisement_banner_cost REAL DEFAULT 999.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed default admin rules if the table is completely fresh
    cursor.execute("SELECT COUNT(*) FROM AdminSettings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO AdminSettings (commission_type, commission_value) VALUES ('Percentage', 10.0)")

    # 2. OWNERS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            owner_id TEXT UNIQUE, 
            name TEXT, 
            mobile TEXT, 
            email TEXT, 
            aadhaar TEXT, 
            profile_photo TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. PROPERTIES TABLE (Requirement 1, 2, 3, 4, 5, 6, 10)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            owner_id TEXT,  -- NOT UNIQUE: One landlord can manage multiple properties cleanly
            property_card_number TEXT DEFAULT 'N/A',
            pg_name TEXT DEFAULT 'N/A', 
            property_type TEXT DEFAULT 'N/A', -- PG, Flat, Office, Chawl, Godown, Shed, Open space
            address TEXT DEFAULT 'N/A',
            facilities TEXT DEFAULT 'N/A',     -- Serialized multi-select list (Wifi, Geyser, etc.)
            property_terms TEXT DEFAULT 'N/A',   -- Property-specific rules (Requirement 10)
            
            -- PG Module Columns (Requirement 3)
            room_ac_type TEXT DEFAULT 'Non-AC', -- AC, Non-AC
            sharing_type TEXT DEFAULT 'Single', -- Single, Double, Triple, Four Sharing
            total_rooms INTEGER DEFAULT 0, 
            total_beds INTEGER DEFAULT 0, 
            occupied_beds INTEGER DEFAULT 0, 
            available_beds INTEGER DEFAULT 1,   -- Updated Default to 1 for standalone unit vacancy mapping
            
            -- Flat / Apartment Module Columns (Requirement 4)
            flat_bhk TEXT DEFAULT 'N/A',
            flat_furnishing TEXT DEFAULT 'N/A',
            flat_ac_status TEXT DEFAULT 'Non-AC',
            flat_parking TEXT DEFAULT 'None',
            flat_security TEXT DEFAULT 'None',
            
            -- Office / Commercial Module Columns (Requirement 5)
            office_cabins INTEGER DEFAULT 0,
            office_workstations INTEGER DEFAULT 0,
            office_meeting_rooms INTEGER DEFAULT 0,
            office_reception_status TEXT DEFAULT 'No',
            office_internet_facility TEXT DEFAULT 'No',
            office_parking_status TEXT DEFAULT 'No',
            
            -- Chawl System Module Columns (Requirement 6)
            chawl_room_number TEXT DEFAULT 'N/A',
            chawl_unit_number TEXT DEFAULT 'N/A',
            chawl_water_connection TEXT DEFAULT 'Shared',
            chawl_electricity_meter_no TEXT DEFAULT 'N/A',
            
            -- Industrial Logistics Warehousing / Open Space Columns
            generic_area_specification TEXT DEFAULT 'N/A',
            FOREIGN KEY(owner_id) REFERENCES Owners(owner_id)
        )
    ''')
    
    # 4. TENANTS TABLE (Requirement 7 & 8)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            tenant_id TEXT UNIQUE, 
            owner_id TEXT, 
            name TEXT, 
            institution TEXT,          -- Standardized column
            father_name TEXT, 
            mother_name TEXT, 
            mobile TEXT, 
            email TEXT, 
            
            -- Document Upload Matrix
            document_type TEXT DEFAULT 'Aadhaar', 
            document_number TEXT DEFAULT 'N/A',
            document_file_path TEXT DEFAULT 'N/A',
            tenant_photo_path TEXT DEFAULT 'N/A',
            
            -- Vehicle Module Mapping Engine
            vehicle_type TEXT DEFAULT 'No Vehicle', 
            vehicle_number TEXT DEFAULT 'N/A',
            
            allocated_unit TEXT DEFAULT 'N/A', 
            permanent_address TEXT DEFAULT 'N/A', 
            current_address TEXT DEFAULT 'N/A', 
            allocated_rent REAL DEFAULT 0.0,
            terms_accepted INTEGER DEFAULT 0,        
            FOREIGN KEY(owner_id) REFERENCES Owners(owner_id)
        )
    ''')

    # 5. RENTAL AGREEMENTS MODULE TABLE (Requirement 9 & 10)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Agreements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agreement_id TEXT UNIQUE NOT NULL,
            owner_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            property_id INTEGER NOT NULL,
            rent_amount REAL DEFAULT 0.0,
            deposit_amount REAL DEFAULT 0.0,
            terms_and_conditions TEXT NOT NULL,
            owner_signature_path TEXT DEFAULT 'N/A',
            tenant_signature_path TEXT DEFAULT 'N/A',
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(owner_id) REFERENCES Owners(owner_id),
            FOREIGN KEY(tenant_id) REFERENCES Tenants(tenant_id),
            FOREIGN KEY(property_id) REFERENCES Properties(id)
        )
    ''')

    # 6. TRANSACTION ACCOUNTING LEDGER TABLE (Requirement 12, 13 & 14)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            owner_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            agreement_id TEXT NOT NULL,
            payment_type TEXT DEFAULT 'Rent',           -- 'Rent' or 'Deposit'
            total_collected REAL DEFAULT 0.0,
            platform_commission REAL DEFAULT 0.0,
            owner_earnings REAL DEFAULT 0.0,
            payment_status TEXT DEFAULT 'Paid',          -- 'Paid', 'Pending', 'Failed'
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(owner_id) REFERENCES Owners(owner_id),
            FOREIGN KEY(tenant_id) REFERENCES Tenants(tenant_id),
            FOREIGN KEY(agreement_id) REFERENCES Agreements(agreement_id)
        )
    ''')

    # 7. MAINTENANCE TICKETS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MaintenanceTickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            tenant_id TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(tenant_id) REFERENCES Tenants(tenant_id),
            FOREIGN KEY(owner_id) REFERENCES Owners(owner_id)
        )
    ''')

    # 8. TECHNICIANS DIRECTORY (New for Service/Invoice Module)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Technicians (
            tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            FOREIGN KEY(owner_id) REFERENCES Owners(owner_id)
        )
    ''')

    # 9. SERVICE LOGS / INVOICE ENGINE (New for Service/Invoice Module)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ServiceLogs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT NOT NULL,
            tech_id INTEGER NOT NULL,
            hours_spent REAL DEFAULT 0.0,
            parts_cost REAL DEFAULT 0.0,
            total_amount REAL DEFAULT 0.0,
            service_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(tech_id) REFERENCES Technicians(tech_id),
            FOREIGN KEY(complaint_id) REFERENCES MaintenanceTickets(ticket_id)
        )
    ''')
    
    conn.commit()
    
    # =====================================================================
    # ⚙️ LIVE MIGRATION VERIFICATION ENGINE (PREVENTS DESYNC CRASHES)
    # =====================================================================
    # Check table structures dynamically to update existing DB footprints seamlessly
    
    # Verification Set A: Owners Layout Sync (Fixes the 500 Internal Server Error)
    cursor.execute("PRAGMA table_info(Owners)")
    owners_cols = [row[1] for row in cursor.fetchall()]
    if "property_type" not in owners_cols:
        cursor.execute("ALTER TABLE Owners ADD COLUMN property_type TEXT DEFAULT 'N/A'")
    if "property_address" not in owners_cols:
        cursor.execute("ALTER TABLE Owners ADD COLUMN property_address TEXT DEFAULT 'N/A'")

        # Verification Set B: Properties Layout Sync
    cursor.execute("PRAGMA table_info(Properties)")
    properties_cols = [row[1] for row in cursor.fetchall()]
    
    if "property_card_no" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN property_card_no TEXT DEFAULT 'N/A'")
    if "property_card_number" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN property_card_number TEXT DEFAULT 'N/A'")
    if "property_terms" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN property_terms TEXT DEFAULT 'N/A'")
    
    # === Flat Fields ===
    if "flat_bhk" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN flat_bhk TEXT DEFAULT 'N/A'")
    if "flat_furnishing" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN flat_furnishing TEXT DEFAULT 'N/A'")
    if "flat_ac_status" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN flat_ac_status TEXT DEFAULT 'Non-AC'")
    if "flat_parking" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN flat_parking TEXT DEFAULT 'None'")
    if "flat_security" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN flat_security TEXT DEFAULT 'None'")
    
    # === Chawl Fields ===
    if "chawl_room_number" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN chawl_room_number TEXT DEFAULT 'N/A'")
    if "chawl_unit_number" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN chawl_unit_number TEXT DEFAULT 'N/A'")
    if "chawl_water_connection" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN chawl_water_connection TEXT DEFAULT 'Shared'")
    if "chawl_electricity_meter_no" not in properties_cols:
        cursor.execute("ALTER TABLE Properties ADD COLUMN chawl_electricity_meter_no TEXT DEFAULT 'N/A'")
    
    # Verification Set C: Tenants Layout Sync
    cursor.execute("PRAGMA table_info(Tenants)")
    tenants_cols = [row[1] for row in cursor.fetchall()]
    if "institution" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN institution TEXT DEFAULT 'N/A'")
    if "identity_document_type" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN identity_document_type TEXT DEFAULT 'Aadhaar'")
    if "id_number" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN id_number TEXT DEFAULT 'N/A'")
    if "document_file_path" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN document_file_path TEXT DEFAULT 'N/A'")
    if "advance_amount" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN advance_amount REAL DEFAULT 0.0")
    if "stay_start_date" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN stay_start_date TEXT DEFAULT 'N/A'")
    if "emergency_contact" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN emergency_contact TEXT DEFAULT 'N/A'")
    if "tenant_contact" not in tenants_cols:
        cursor.execute("ALTER TABLE Tenants ADD COLUMN tenant_contact TEXT DEFAULT 'N/A'")

    # Verification Set D: MaintenanceTickets Layout Sync
    cursor.execute("PRAGMA table_info(MaintenanceTickets)")
    tickets_cols = [row[1] for row in cursor.fetchall()]
    if "technician_id" not in tickets_cols:
        cursor.execute("ALTER TABLE MaintenanceTickets ADD COLUMN technician_id INTEGER DEFAULT NULL")
    
    # (Set E: Technicians Layout Sync)
    cursor.execute("PRAGMA table_info(Technicians)")
    tech_cols = [row[1] for row in cursor.fetchall()]
    if "contact_number" not in tech_cols:
        cursor.execute("ALTER TABLE Technicians ADD COLUMN contact_number TEXT DEFAULT 'N/A'")
    if "owner_id" not in tech_cols:
        cursor.execute("ALTER TABLE Technicians ADD COLUMN owner_id TEXT DEFAULT 'NONE'")
    
    # Verification Set F: ServiceLogs Layout Sync
    cursor.execute("PRAGMA table_info(ServiceLogs)")
    logs_cols = [row[1] for row in cursor.fetchall()]
    if "parts_description" not in logs_cols:
        cursor.execute("ALTER TABLE ServiceLogs ADD COLUMN parts_description TEXT DEFAULT 'No parts used'")
    if "parts_cost" not in logs_cols:
        cursor.execute("ALTER TABLE ServiceLogs ADD COLUMN parts_cost REAL DEFAULT 0.0")

    conn.commit()
    conn.close()

def generate_unique_id(prefix):
    conn = get_db_connection()
    cursor = conn.cursor()
    if prefix == "OWN":
        cursor.execute("SELECT owner_id FROM Owners ORDER BY id DESC LIMIT 1")
    elif prefix == "TEN":
        cursor.execute("SELECT tenant_id FROM Tenants ORDER BY id DESC LIMIT 1")
    elif prefix == "TKT":
        cursor.execute("SELECT ticket_id FROM MaintenanceTickets ORDER BY id DESC LIMIT 1")
    elif prefix == "AGR":
        cursor.execute("SELECT agreement_id FROM Agreements ORDER BY id DESC LIMIT 1")
    elif prefix == "TXN":
        cursor.execute("SELECT transaction_id FROM Transactions ORDER BY id DESC LIMIT 1")
    else:
        return f"{prefix}-000001"
        
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return f"{prefix}-000001"
    
    last_id = row[0]
    try:
        current_num = int(last_id.split("-")[1])
        return f"{prefix}-{(current_num + 1):06d}"
    except:
        return f"{prefix}-000001"