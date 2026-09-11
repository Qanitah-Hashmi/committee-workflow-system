from database import get_connection

def get_visible_committees(user):
    """Get committees visible to a user based on visibility rules"""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        role = user.get('role')
        school = user.get('school')
        department = user.get('department')

        if role == 'Faculty':
          
            query = """
                SELECT * FROM committees
                WHERE status IN ('Open', 'Under Review', 'Filled', 'Active')
                AND (
                    (level = 'University'
                        AND (school IS NULL OR school = '')
                        AND (department IS NULL OR department = ''))
                    OR (level = 'School' AND school = ?)
                    OR (level = 'Department' AND department = ?)
                )
                ORDER BY created_at DESC
            """
            cursor.execute(query, (school, department))

        elif role in ('Rector', 'President', 'Registrar', 'System Admin'):
  
            query = "SELECT * FROM committees ORDER BY created_at DESC"
            cursor.execute(query)

        elif role == 'Dean':
 
            query = """
                SELECT * FROM committees
                WHERE
                    (level = 'University'
                        AND (school IS NULL OR school = '')
                        AND (department IS NULL OR department = ''))
                    OR (level = 'School' AND school = ?)
                    OR (level = 'Department' AND school = ?)
                ORDER BY created_at DESC
            """
            cursor.execute(query, (school, school))

        else:

            query = """
                SELECT * FROM committees
                WHERE (
                    status IN ('Open', 'Under Review', 'Filled', 'Active')
                    AND (
                        (level = 'University'
                            AND (school IS NULL OR school = '')
                            AND (department IS NULL OR department = ''))
                        OR (level = 'School' AND school = ?)
                        OR (level = 'Department' AND department = ?)
                    )
                )
                OR (
                    status IN ('Draft', 'Pending Approval', 'Approved')
                    AND level = 'Department' AND department = ?
                )
                ORDER BY created_at DESC
            """
            cursor.execute(query, (school, department, department))

        committees = [dict(row) for row in cursor.fetchall()]
        return committees
    finally:
        conn.close()