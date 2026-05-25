from src.screens.database.config import supabase

import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(),bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_teacher_exsits(username):
    ## Checks if the teacher with the given username exists in the database
    response = supabase.table('teachers').select('username').eq('username', username).execute()
    return len(response.data) > 0

def create_teacher(username, password, name):
    ## Creates a new teacher in the database with the given username, password and name
    data = {
        'username': username,
        'password':hash_pass(password),
        'name': name
        }
    
    response = supabase.table('teachers').insert(data).execute()
    return response.data

def teacher_login(username, password):
    ## Checks if the teacher with the given username and password exists in the database
    response = supabase.table('teachers').select('*').eq('username', username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return  teacher
        
    return None

def get_all_students():
    ## Fetches all the students from the database
    response = supabase.table('students').select('*').execute()
    return response.data