import sqlite3
import hashlib
from datetime import datetime
import time

DB_NAME = "committee_workplace.db"

def get_connection():
    """Get database connection with timeout and retry"""
    try:
        conn = sqlite3.connect(DB_NAME, timeout=20)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn
    except sqlite3.OperationalError as e:
        print(f"Database connection error: {e}")
        raise e

def _add_column_if_missing(cursor, table, column, definition):
    """Add a column to an existing table if it doesn't exist (safe migration)"""
    cursor.execute(f"PRAGMA table_info({table})")
    existing = [row[1] for row in cursor.fetchall()]
    if column not in existing:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

def init_database():
    """Initialize database with all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Faculty', 'Department Coordinator', 'HOD', 'Dean', 'Registrar', 'Rector', 'President', 'System Admin')),
            department TEXT,
            school TEXT,
            rank TEXT,
            created_at TEXT NOT NULL,
            locked INTEGER DEFAULT 0,
            last_login TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS committees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL CHECK(level IN ('University', 'School', 'Department')),
            type TEXT NOT NULL,
            hours_per_week INTEGER NOT NULL,
            duration_months INTEGER NOT NULL,
            total_seats INTEGER DEFAULT 0,
            filled_seats INTEGER DEFAULT 0,
            status TEXT NOT NULL CHECK(status IN ('Draft', 'Pending Approval', 'Approved', 'Open', 'Under Review', 'Filled', 'Active', 'Closed', 'Archived', 'Cancelled')) DEFAULT 'Draft',
            school TEXT,
            department TEXT,
            created_by INTEGER,
            created_on_behalf_of INTEGER,
            initiating_authority INTEGER,
            approving_authority INTEGER,
            publishing_authority INTEGER,
            deadline TEXT NOT NULL,
            description TEXT,
            requirements TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (created_on_behalf_of) REFERENCES users(id),
            FOREIGN KEY (initiating_authority) REFERENCES users(id),
            FOREIGN KEY (approving_authority) REFERENCES users(id),
            FOREIGN KEY (publishing_authority) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS committee_composition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            committee_id INTEGER NOT NULL,
            rank_required TEXT NOT NULL,
            total_slots INTEGER NOT NULL,
            filled_slots INTEGER DEFAULT 0,
            FOREIGN KEY (committee_id) REFERENCES committees(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            committee_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Submitted', 'Under Review', 'Accepted', 'Rejected', 'Withdrawn', 'Waitlisted', 'Closed without Selection')) DEFAULT 'Submitted',
            rank_at_application TEXT,
            applied_date TEXT NOT NULL,
            updated_date TEXT,
            rejection_reason TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (committee_id) REFERENCES committees(id) ON DELETE CASCADE,
            UNIQUE(user_id, committee_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS committee_roster (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            committee_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role_in_committee TEXT CHECK(role_in_committee IN ('Chair', 'Convener', 'Secretary', 'Member', 'Ex-officio')) DEFAULT 'Member',
            assignment_type TEXT CHECK(assignment_type IN ('Applied', 'Direct')) DEFAULT 'Applied',
            join_date TEXT NOT NULL,
            end_date TEXT,
            status TEXT CHECK(status IN ('Active', 'Completed', 'Removed')) DEFAULT 'Active',
            removal_reason TEXT,
            FOREIGN KEY (committee_id) REFERENCES committees(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(committee_id, user_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('info', 'success', 'warning', 'error')) DEFAULT 'info',
            created_at TEXT NOT NULL,
            read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # ==================== MIGRATIONS FOR EXISTING DATABASES ====================
    _add_column_if_missing(cursor, 'committees', 'total_seats', 'INTEGER DEFAULT 0')
    _add_column_if_missing(cursor, 'committees', 'filled_seats', 'INTEGER DEFAULT 0')

    # Normalize empty strings to NULL
    cursor.execute("UPDATE committees SET school = NULL WHERE school = ''")
    cursor.execute("UPDATE committees SET department = NULL WHERE department = ''")
    cursor.execute("UPDATE committees SET school = NULL, department = NULL WHERE level = 'University'")
    cursor.execute("UPDATE committees SET department = NULL WHERE level = 'School'")

    # Backfill seat counters
    cursor.execute('''
        UPDATE committees SET total_seats = COALESCE((
            SELECT SUM(total_slots) FROM committee_composition
            WHERE committee_id = committees.id), 0)
    ''')
    cursor.execute('''
        UPDATE committees SET filled_seats = COALESCE((
            SELECT SUM(filled_slots) FROM committee_composition
            WHERE committee_id = committees.id), 0)
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== USER OPERATIONS ====================
def create_user(email, password, name, role, department=None, school=None, rank=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (email, password_hash, name, role, department, school, rank, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, hash_password(password), name, role, department, school, rank, datetime.now().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def verify_user(email, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, name, role, department, school, rank, locked
            FROM users
            WHERE email = ? AND password_hash = ?
        ''', (email, hash_password(password)))
        user = cursor.fetchone()
        if user and not user['locked']:
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now().isoformat(), user['id']))
            conn.commit()
            return dict(user)
        return None
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_all_users(role=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if role:
            cursor.execute('SELECT * FROM users WHERE role = ?', (role,))
        else:
            cursor.execute('SELECT * FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        return users
    finally:
        conn.close()

def lock_user(email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET locked = 1 WHERE email = ?', (email,))
        conn.commit()
    finally:
        conn.close()

# ==================== AUDIT LOG ====================
def log_audit(user_id, action, target_type=None, target_id=None, details=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (user_id, action, target_type, target_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, action, target_type, target_id, details, datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"Audit log error: {e}")
    finally:
        conn.close()

def get_audit_logs(limit=100):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.name as user_name, u.role as user_role 
            FROM audit_logs a 
            LEFT JOIN users u ON a.user_id = u.id 
            ORDER BY a.created_at DESC LIMIT ?
        ''', (limit,))
        logs = [dict(row) for row in cursor.fetchall()]
        return logs
    finally:
        conn.close()

# ==================== COMMITTEE OPERATIONS ====================
def create_committee(data, created_by_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Normalize scope
        school = (data.get('school') or '').strip() or None
        department = (data.get('department') or '').strip() or None
        if data['level'] == 'University':
            school, department = None, None
        elif data['level'] == 'School':
            department = None

        total_seats = sum(slots for slots in data.get('composition', {}).values() if slots and slots > 0)

        cursor.execute('''
            INSERT INTO committees (name, level, type, hours_per_week, duration_months, total_seats, filled_seats, status,
                                    school, department, created_by, created_on_behalf_of, initiating_authority,
                                    approving_authority, publishing_authority, deadline, description, requirements, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, 'Draft', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['level'], data['type'], data['hours'], data['duration'], total_seats,
              school, department, created_by_id, data.get('on_behalf_of'),
              data.get('initiating_auth'), data.get('approving_auth'), data.get('publishing_auth'),
              data['deadline'], data.get('description'), data.get('requirements'),
              datetime.now().isoformat()))
        committee_id = cursor.lastrowid
        
        for rank, slots in data.get('composition', {}).items():
            if slots > 0:
                cursor.execute('''
                    INSERT INTO committee_composition (committee_id, rank_required, total_slots)
                    VALUES (?, ?, ?)
                ''', (committee_id, rank, slots))
        
        conn.commit()
        
        try:
            log_audit(created_by_id, "Created Committee", "committee", committee_id, f"Name: {data['name']}")
        except:
            pass
            
        return committee_id
    except Exception as e:
        print(f"Create committee error: {e}")
        return None
    finally:
        conn.close()

def get_committee_by_id(committee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM committees WHERE id = ?', (committee_id,))
        committee = cursor.fetchone()
        return dict(committee) if committee else None
    finally:
        conn.close()

def get_all_committees(status=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute('SELECT * FROM committees WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM committees ORDER BY created_at DESC')
        committees = [dict(row) for row in cursor.fetchall()]
        return committees
    finally:
        conn.close()

def update_committee_status(committee_id, status, user_id, details=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE committees SET status = ? WHERE id = ?', (status, committee_id))
        conn.commit()
        try:
            log_audit(user_id, f"Updated Committee Status to {status}", "committee", committee_id, details)
        except:
            pass
    finally:
        conn.close()

def update_committee(committee_id, data, user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE committees SET 
                name = ?, description = ?, hours_per_week = ?, duration_months = ?, 
                deadline = ?, requirements = ?, type = ?, level = ?, school = ?, department = ?
            WHERE id = ?
        ''', (data['name'], data['description'], data['hours'], data['duration'],
              data['deadline'], data['requirements'], data['type'], data['level'],
              data.get('school'), data.get('department'), committee_id))
        conn.commit()
        try:
            log_audit(user_id, "Updated Committee", "committee", committee_id, f"Name: {data['name']}")
        except:
            pass
    finally:
        conn.close()

def get_committee_composition(committee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM committee_composition WHERE committee_id = ?', (committee_id,))
        comp = [dict(row) for row in cursor.fetchall()]
        return comp
    finally:
        conn.close()

def update_committee_composition_slot(composition_id, filled_slots):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE committee_composition SET filled_slots = ? WHERE id = ?', (filled_slots, composition_id))
        conn.commit()
    finally:
        conn.close()

def check_slot_availability(committee_id, rank):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, filled_slots, total_slots FROM committee_composition 
            WHERE committee_id = ? AND (rank_required = ? OR rank_required = 'Any')
            AND filled_slots < total_slots
        ''', (committee_id, rank))
        return cursor.fetchone()
    finally:
        conn.close()

# ==================== APPLICATION OPERATIONS ====================
def create_application(user_id, committee_id, rank):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO applications (user_id, committee_id, rank_at_application, applied_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, committee_id, rank, datetime.now().isoformat()))
        app_id = cursor.lastrowid
        conn.commit()
        try:
            log_audit(user_id, "Applied to Committee", "committee", committee_id)
        except:
            pass
        return app_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_applications(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, c.name as committee_name, c.level, c.hours_per_week 
            FROM applications a 
            JOIN committees c ON a.committee_id = c.id 
            WHERE a.user_id = ?
            ORDER BY a.applied_date DESC
        ''', (user_id,))
        apps = [dict(row) for row in cursor.fetchall()]
        return apps
    finally:
        conn.close()

def get_committee_applications(committee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.name, u.department, u.school, u.rank, u.role 
            FROM applications a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.committee_id = ?
            ORDER BY a.applied_date DESC
        ''', (committee_id,))
        apps = [dict(row) for row in cursor.fetchall()]
        return apps
    finally:
        conn.close()

def update_application_status(app_id, status, reviewer_id, reason=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM applications WHERE id = ?', (app_id,))
        app = dict(cursor.fetchone())
        
        cursor.execute('''
            UPDATE applications SET status = ?, updated_date = ?, rejection_reason = ?
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), reason, app_id))
        
        if status == 'Accepted':
            cursor.execute('''
                INSERT INTO committee_roster (committee_id, user_id, assignment_type, join_date)
                VALUES (?, ?, 'Applied', ?)
            ''', (app['committee_id'], app['user_id'], datetime.now().isoformat()))

            # FIXED: Pass rank twice for ORDER BY
            cursor.execute('''
                SELECT id FROM committee_composition
                WHERE committee_id = ? AND (rank_required = ? OR rank_required = 'Any')
                AND filled_slots < total_slots
                ORDER BY CASE WHEN rank_required = ? THEN 0 ELSE 1 END
                LIMIT 1
            ''', (app['committee_id'], app['rank_at_application'], app['rank_at_application']))
            slot = cursor.fetchone()
            if slot:
                cursor.execute('UPDATE committee_composition SET filled_slots = filled_slots + 1 WHERE id = ?', (slot['id'],))
            cursor.execute('UPDATE committees SET filled_seats = filled_seats + 1 WHERE id = ?', (app['committee_id'],))

        conn.commit()
        try:
            log_audit(reviewer_id, f"Application {status}", "application", app_id, reason)
        except:
            pass
    finally:
        conn.close()

def withdraw_application(user_id, committee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE applications SET status = 'Withdrawn', updated_date = ?
            WHERE user_id = ? AND committee_id = ? AND status IN ('Submitted', 'Under Review')
        ''', (datetime.now().isoformat(), user_id, committee_id))
        conn.commit()
        try:
            log_audit(user_id, "Withdrew Application", "committee", committee_id)
        except:
            pass
    finally:
        conn.close()

def is_user_already_applied(user_id, committee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM applications 
            WHERE user_id = ? AND committee_id = ? AND status NOT IN ('Withdrawn', 'Rejected', 'Closed without Selection')
        ''', (user_id, committee_id))
        return cursor.fetchone() is not None
    finally:
        conn.close()

# ==================== ROSTER & SERVICE HISTORY ====================

def direct_assign_member(committee_id, user_id, role, assigner_id, reason):
    """Directly assign a member to a committee"""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Check if already in roster for this committee
        cursor.execute('''
            SELECT id FROM committee_roster WHERE committee_id = ? AND user_id = ? AND status = 'Active'
        ''', (committee_id, user_id))
        if cursor.fetchone():
            return False, "User is already a member of this committee"

        # Get user rank
        cursor.execute('SELECT rank FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        user_rank = user_row['rank'] if user_row and user_row['rank'] else 'Any'

        # FIXED: Pass rank twice for ORDER BY
        cursor.execute('''
            SELECT id, filled_slots, total_slots FROM committee_composition
            WHERE committee_id = ? AND (rank_required = ? OR rank_required = 'Any')
            AND filled_slots < total_slots
            ORDER BY CASE WHEN rank_required = ? THEN 0 ELSE 1 END
            LIMIT 1
        ''', (committee_id, user_rank, user_rank))
        slot = cursor.fetchone()

        # If no slot is available, create a new 'Any' slot
        if not slot:
            cursor.execute('''
                INSERT INTO committee_composition (committee_id, rank_required, total_slots, filled_slots)
                VALUES (?, 'Any', 1, 0)
            ''', (committee_id,))
            slot_id = cursor.lastrowid
            cursor.execute('UPDATE committees SET total_seats = total_seats + 1 WHERE id = ?', (committee_id,))
        else:
            slot_id = slot['id']

        # Add to roster
        cursor.execute('''
            INSERT INTO committee_roster (committee_id, user_id, role_in_committee, assignment_type, join_date)
            VALUES (?, ?, ?, 'Direct', ?)
        ''', (committee_id, user_id, role, datetime.now().isoformat()))

        # Update slot and committee seat counters
        cursor.execute('UPDATE committee_composition SET filled_slots = filled_slots + 1 WHERE id = ?', (slot_id,))
        cursor.execute('UPDATE committees SET filled_seats = filled_seats + 1 WHERE id = ?', (committee_id,))

        conn.commit()
        try:
            log_audit(assigner_id, "Direct Assignment", "committee", committee_id,
                      f"User: {user_id}, Role: {role}, Reason: {reason}")
        except Exception:
            pass
        return True, "Assigned successfully"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_committee_roster(committee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name, u.department, u.school, u.rank, u.email
            FROM committee_roster r
            JOIN users u ON r.user_id = u.id
            WHERE r.committee_id = ?
            ORDER BY r.join_date
        ''', (committee_id,))
        roster = [dict(row) for row in cursor.fetchall()]
        return roster
    finally:
        conn.close()

def remove_committee_member(committee_id, user_id, remover_id, reason):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE committee_roster SET status = 'Removed', end_date = ?, removal_reason = ?
            WHERE committee_id = ? AND user_id = ? AND status = 'Active'
        ''', (datetime.now().isoformat(), reason, committee_id, user_id))

        cursor.execute('''
            SELECT id FROM committee_composition
            WHERE committee_id = ? AND filled_slots > 0
            LIMIT 1
        ''', (committee_id,))
        slot = cursor.fetchone()
        if slot:
            cursor.execute('UPDATE committee_composition SET filled_slots = filled_slots - 1 WHERE id = ?', (slot['id'],))
        cursor.execute('UPDATE committees SET filled_seats = MAX(filled_seats - 1, 0) WHERE id = ?', (committee_id,))

        conn.commit()
        try:
            log_audit(remover_id, "Removed Member", "committee", committee_id, f"User: {user_id}, Reason: {reason}")
        except:
            pass
        return True
    finally:
        conn.close()

def get_user_service_history(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, c.name as committee_name, c.level, c.hours_per_week, c.duration_months
            FROM committee_roster r 
            JOIN committees c ON r.committee_id = c.id 
            WHERE r.user_id = ?
            ORDER BY r.join_date DESC
        ''', (user_id,))
        history = [dict(row) for row in cursor.fetchall()]
        return history
    finally:
        conn.close()

def is_user_already_member(user_id, committee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM committee_roster 
            WHERE committee_id = ? AND user_id = ? AND status = 'Active'
        ''', (committee_id, user_id))
        return cursor.fetchone() is not None
    finally:
        conn.close()

# ==================== NOTIFICATIONS ====================
def create_notification(user_id, message, type='info'):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, message, type, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message, type, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()

def get_user_notifications(user_id, unread_only=False):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if unread_only:
            cursor.execute('''
                SELECT * FROM notifications
                WHERE user_id = ? AND read = 0
                ORDER BY created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT * FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (user_id,))
        notifications = [dict(row) for row in cursor.fetchall()]
        return notifications
    finally:
        conn.close()

def mark_notifications_read(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE notifications SET read = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
    finally:
        conn.close()

def clear_notifications(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))
        conn.commit()
    finally:
        conn.close()

# ==================== DUMMY DATA ====================
def insert_dummy_data():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] > 0:
            print("ℹ️ Dummy data already exists. Skipping...")
            return

        users = [
            ('faculty1@uni.edu', 'pass123', 'Dr. Alan Turing', 'Faculty', 'Computer Science', 'Engineering', 'Assistant Professor'),
            ('faculty2@uni.edu', 'pass123', 'Dr. Ada Lovelace', 'Faculty', 'Business', 'Business', 'Associate Professor'),
            ('faculty3@uni.edu', 'pass123', 'Dr. Grace Hopper', 'Faculty', 'Computer Science', 'Engineering', 'Professor'),
            ('coord1@uni.edu', 'pass123', 'Mr. John Doe', 'Department Coordinator', 'Computer Science', 'Engineering', None),
            ('hod1@uni.edu', 'pass123', 'Prof. Jane Smith', 'HOD', 'Computer Science', 'Engineering', 'Professor'),
            ('dean1@uni.edu', 'pass123', 'Prof. Robert Brown', 'Dean', None, 'Engineering', 'Professor'),
            ('registrar@uni.edu', 'pass123', 'Ms. Emily Davis', 'Registrar', None, None, None),
            ('rector@uni.edu', 'pass123', 'Dr. Michael Johnson', 'Rector', None, None, None),
            ('president@uni.edu', 'pass123', 'Dr. Sarah Wilson', 'President', None, None, None)
        ]
        
        for email, pwd, name, role, dept, school, rank in users:
            cursor.execute('''
                INSERT INTO users (email, password_hash, name, role, department, school, rank, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, hash_password(pwd), name, role, dept, school, rank, datetime.now().isoformat()))
            
        conn.commit()
        print("✅ Dummy data inserted successfully!")
        print("\n📋 DEMO CREDENTIALS:")
        print("=" * 40)
        print("ADMINS:")
        print("  📧 hod1@uni.edu / pass123 (HOD, CS Dept)")
        print("  📧 dean1@uni.edu / pass123 (Dean, Engineering)")
        print("  📧 registrar@uni.edu / pass123")
        print("  📧 rector@uni.edu / pass123")
        print("  📧 president@uni.edu / pass123")
        print("\nFACULTY:")
        print("  📧 faculty1@uni.edu / pass123 (CS, Asst. Prof)")
        print("  📧 faculty2@uni.edu / pass123 (Business, Assoc. Prof)")
        print("  📧 faculty3@uni.edu / pass123 (CS, Professor)")
        print("\nCOORDINATOR:")
        print("  📧 coord1@uni.edu / pass123 (CS Dept)")
        print("=" * 40)
    finally:
        conn.close()