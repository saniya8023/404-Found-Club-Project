import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="izma123", 
        database="hackathon_model"
    )

def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    
    cursor = conn.cursor(dictionary=True, buffered=True) 
    
    result = None
    try:
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
        
        
        if not fetch:
            conn.commit()
            
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback() 
    finally:
       
        cursor.close()
        conn.close()
        
    return result