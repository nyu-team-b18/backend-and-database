from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import oracledb

app = Flask(__name__)
CORS(app)
session = {}

cs = '''(description= (retry_count=3)(retry_delay=3)(address=(protocol=tcps)
        (port=1521)(host=adb.us-ashburn-1.oraclecloud.com))
        (connect_data=(service_name=g4ce17c11a5179b_helloadventuredb_low.adb.oraclecloud.com))
        (security=(ssl_server_dn_match=yes)))'''

conn = oracledb.connect(
    user="admin",
    password="Helloadventure123!",
    dsn=cs)  # the connection string copied from the cloud console


@app.route('/verifyRegistration', methods=["GET", "POST"])
def verifyRegistration():
    global session

    # Get registration details
    data = request.get_json()
    account_type = data['account-type']
    name = data['name']
    email = data['email']
    username = data['username']
    password = data['password']
    confirmation = data['password-confirm']

    # Check if passwords match
    if password != confirmation:
        return jsonify({
            "result": "FAIL",
            "message": "Passwords must match"
        })

    # Register admin account
    if account_type == "admin":
        # Get student group
        student_group = data['student-group']   

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE email =: temp', temp=email)
        data = cursor.fetchall()

        # If the account exists
        if data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "User already exists"
            })

        # Check if the student group is in use
        cursor.execute('SELECT * FROM admin WHERE student_group =: temp', temp=student_group)
        data = cursor.fetchall()

        # If the student group is in use
        if data:    
            cursor.close()
            return jsonify({
                "result": "FAIL", 
                "message": "Student group in use"
            })

        # Create the account
        cursor.execute('INSERT INTO admin (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP, NAME) '
                        'VALUES(:email, :username, :password, :student_group, :name)',
                        [email, username, password, student_group, name])
        conn.commit()
        cursor.close()

        # Begin new session
        session['username'] = username
        session['email'] = email
        session['name'] = name
        session['account-type'] = account_type

        return jsonify({
            "result": "SUCCEED"
        })

    elif account_type == "student":
        # Get student group
        student_group = data['student-group']   

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM student WHERE email =: temp', temp=email)
        data = cursor.fetchone()

        # If the account exists
        if data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "User already exists"
            })

        # Check if the student group exists
        cursor.execute('SELECT * FROM admin WHERE student_group =: temp', temp=student_group)
        data = cursor.fetchall()

        # If the student group exists
        if not data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "Student group not found"
            })

        # Create the account
        cursor.execute('INSERT INTO student (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP, PROGRESS, ASSIGNMENT, NAME) '
                        'VALUES(:email, :username, :password, :student_group, null, null, :name)',
                        [email, username, password, student_group, name])
        conn.commit()
        cursor.close()

        # Begin a new session
        session['username'] = username
        session['email'] = email
        session['name'] = name
        session['account-type'] = account_type

        return jsonify({
            "result": "SUCCEED",
        })

    elif account_type == "guest":
        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE email =: temp', temp=email)
        data = cursor.fetchall()

        # If the account exists
        if data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "User already exists"
            })  

        # Create the account
        cursor.execute('INSERT INTO guest (EMAIL, USER_NAME, PASSWORD, PROGRESS, NAME) '
                        'VALUES(:email, :username, :password, null, :name)',
                        [email, username, password, name])
        
        # Begin new session
        session['username'] = username
        session['email'] = email
        session['name'] = name
        session['account-type'] = account_type

        conn.commit()
        cursor.close()
        return jsonify({
            "result": "SUCCEED",
        })


@app.route('/verifyLogin', methods=["GET", "POST"])
def verifyLogin():
    global session

    data = request.get_json()
    # account_type = data['account-type']
    username = data['username']
    password = data['password']

    username_index = 1

    # CHECK IF IT IS AN ADMIN ACCOUNT
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE user_name =: username and password =: password', [username, password])
    data = cursor.fetchone()

    print(data)

    if data:
        cursor.close()
        student_group_index = 3
        name_index = 4
        session['account-type'] = 'admin'
        session['username'] = data[username_index]
        session['student-group'] = data[student_group_index]
        session['name'] = data[name_index]
        
        return jsonify({}), 200
    
    # CHECK IF IT IS A STUDENT ACCOUNT
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM student WHERE user_name =: username and password =: password', [username, password])
    data = cursor.fetchone()

    if data:
        cursor.close()
        student_group_index = 5
        name_index = 6
        session['account-type'] = 'student'
        session['username'] = data[username_index]
        session['student-group'] = data[student_group_index]
        session['name'] = data[name_index]

        return jsonify({}), 200

    # CHECK IF IT IS A GUEST ACCOUNT
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM guest WHERE user_name =: username and password =: password', [username, password])
    data = cursor.fetchone()

    if data:
        cursor.close()
        name_index = 4
        session['account-type'] = 'guest'
        session['username'] = data[username_index]
        session['name'] = data[name_index]
        return jsonify({}), 200

    # Login failed
    return jsonify({}), 409


@app.route('/logout', methods=["GET", "POST"])
def logout():
    global session
    session.clear()
    
    # redirect
    return jsonify({})


@app.route('/getAssignments', methods=["GET"])
def getAssignments():
    global session
    # Get the student group
    student_group = session['student-group']

    # Get class assignments
    cursor = conn.cursor()
    cursor.execute('SELECT assign_title from ASSIGNMENT WHERE student_group =: temp', temp = student_group)
    data = cursor.fetchall()

    return jsonify({
        'assignments': data,
    })


@app.route('/getStudents', methods=["GET"])
def getStudents():
    global session

    # Get class students
    student_group = session['student-group']
    cursor = conn.cursor()

    cursor.execute('SELECT user_name FROM STUDENT where student_group =: student_group', student_group = student_group)
    data = cursor.fetchall() # a list of students
    cursor.close()

    # Get all student usernames
    student_list = []
    for student in data:
        student_list.append({
            'username': student[0],
            'name': student[0]
        })
    
    return jsonify({
        'students': student_list
    })


@app.route('/getAccountType', methods=["GET"])
def getAccountType():
    global session

    # Get account type & name
    try:
        account_type = session['account-type']
        name = session['name']
    except:
        account_type = 'none'
        name = 'none'

    return jsonify({
        'account-type': account_type,
        'name': name
    })


@app.route('/getAssignmentDetails', methods=["GET"])
def getAssignmentDetails():
    global session
    student_group = session['student-group']

    # GET args
    assign_title = request.args.get('assignment')

    # Get assignment description and date
    cursor = conn.cursor()
    # check if the assignment exists
    cursor.execute('SELECT * from assignment WHERE assign_title =: assign_title AND student_group =: student_group ', [assign_title, student_group])
    data = cursor.fetchall()
    
    return jsonify({
        'title': assign_title,
        'description': data[0][0],
        'date': data[0][1].strftime('%Y-%m-%d'),
        'world': data[0][2],
        'level': data[0][3]
    })


@app.route('/updateAssignment', methods=["GET", "POST"])
def updateAssignment():
    if (request.method == 'POST'):
        global session
        student_group = session['student-group']

        data = request.get_json()
        assign_title = data['title']
        assign_description = data['description']
        due_date = data['date']
        world = data['world']
        game_level = data['level']

        # Update the assignment
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE ASSIGNMENT SET assign_description =: assign_description, due_date = TO_DATE(:due_date, 'YYYY-MM-DD'), world =: world, game_level =: game_level
            WHERE assign_title =: assign_title AND student_group =: student_group""", [assign_description, due_date, world, game_level, assign_title, student_group])
        conn.commit()
        cursor.close()

    return jsonify({})


@app.route('/createAssignment', methods=["GET", "POST"])
def createAssignment():
    global session
    student_group = session['student-group']

    data = request.get_json()
    assign_title = data['title']
    assign_description = data['description']
    due_date = data['date']
    world = data['world']
    game_level = data['level']
    
    cursor = conn.cursor()
    # check if the assignment already exists
    cursor.execute('SELECT * from assignment where assign_title =: title AND student_group =: student_group', 
                   [assign_title, student_group])
    data = cursor.fetchone()

    if data:  # Failure, assignment already exists
        cursor.close()
        return jsonify({}), 409

    else:  # Success
        cursor.execute(f"""INSERT into assignment(assign_description, due_date, world, game_level, student_group, assign_title) 
                            VALUES(:assign_description, TO_DATE(:due_date, 'YYYY-MM-DD'), :world, :game_level, :student_group, :assign_title)""",
                       [assign_description, due_date, world, game_level, student_group, assign_title])
        conn.commit()
        cursor.close()
        return jsonify({}), 200


@app.route('/getIncompleteAssignments', methods=["GET"])
def getIncompleteAssignments():
    # Assume account type is student

    username = session['username']

    cursor = conn.cursor()
    cursor.execute("""SELECT ASSIGNMENT.ASSIGN_TITLE from student, assignment 
                        WHERE student.progress <= assignment.game_level
                        AND student.student_group = assignment.student_group
                        AND student.user_name =: temp""", [username])
    incomplete_raw = cursor.fetchall()
    cursor.close()
    incomplete = []
    for assignment in incomplete_raw:
        incomplete.append(assignment[0])
        return jsonify({
        'assignments': incomplete
    })



@app.route('/getProfile', methods=["GET"])
def getProfile():
    account_type = session['account-type']
    username = session['username']
    cursor = conn.cursor()

    details = {}

    if account_type == 'student':
        # Get the account details

        cursor.execute('SELECT user_name, email, progress, name, bio from student where user_name =: temp', temp=username)
        data = cursor.fetchone()
        error = None
        cursor.close()
        if (data):
            details = {
                'username': data[0],
                'email': data[1],
                'progress': data[2],
                'name': data[3],
                'bio': data[4]
            }
    elif account_type == 'admin':
        # Get the account details

        cursor.execute('SELECT user_name, email, name, bio from admin where user_name =: temp', temp=username)
        data = cursor.fetchone()
        data = list(data)
        for ndx in range(len(data)):
            if data[ndx] is None: data[ndx] = 'None'
        cursor.close()
        if (data):
            details = {
                'username': data[0],
                'email': data[1],
                'name': data[2],
                'bio': data[3]
            }
    else:
        # Get the account details
        cursor.execute('SELECT user_name, email, progress, name, bio from guest where user_name =: temp', temp=username)
        data = cursor.fetchone()
        error = None
        cursor.close()
        if (data):
            details = {
                'username': data[0],
                'email': data[1],
                'progress': data[2],
                'name': data[3],
                'bio': data[4]
            }

    return jsonify(details)


@app.route('/updateProfile', methods=['GET', 'POST'])
def updateProfile():
    global session

    account_type = session['account-type']
    username = session['username']

    data = request.get_json()
    new_email = data['email']
    new_name = data['name']
    new_bio = data['bio']

    cursor = conn.cursor()

    if account_type == 'student':
        # Update the account details
        cursor.execute('update STUDENT set email =: new_email, name =: new_name, bio =: new_bio'
                        ' where user_name =: username', [new_email, new_name, new_bio, username])
    elif account_type == 'admin':
        # Update the account details
        cursor.execute('update ADMIN set email =: new_email, name =: new_name, bio =: new_bio'
                        ' where user_name =: username', [new_email, new_name, new_bio, username])
    else:
        # Get the account details
        print(new_bio)
        cursor.execute('update GUEST set email =: new_email, name =: new_name, bio =: new_bio'
                        ' where user_name =: username', [new_email, new_name, new_bio, username])
    

    session['email'] = new_email
    session['name'] = new_name

    conn.commit()
    cursor.close()

    return jsonify({})


@app.route("/deleteAccount", methods=["GET", "DELETE"])
def deleteAccount():
    global session

    # Get account details
    account_type = session['account-type']
    username = session['username']

    cursor = conn.cursor()
    if account_type == 'admin':
        # # TODO: Change all students under this admin to guest accounts
        # #check if the student exists and is in thr group
        # cursor.execute('SELECT student.user_name from student, admin WHERE student.student_group = admin.student_group'
        #                'AND admin.user_name =: temp', temp = username)
        # data = cursor.fetchall()
        # if data:
        #     for student in data:
        #         cursor.execute('UPDATE student SET student_group = null WHERE user_name =: temp', temp = student[0])
        #         conn.commit()
        cursor.execute('DELETE FROM admin WHERE user_name =: temp', temp = username)
        conn.commit()
        cursor.close()
    elif account_type == 'guest':
        cursor.execute('DELETE FROM guest WHERE user_name =: temp', temp = username)
        conn.commit()
        cursor.close()


    # Destroy all session variables
    session.clear()
    return jsonify({})


@app.route("/getStudentInformation", methods=["GET"])
def getStudentInformation():
    # GET args
    student_username = request.args.get('username')
    student_group = session['student-group']
    cursor = conn.cursor()
    # Get student information
    cursor.execute('SELECT email, name, bio FROM STUDENT where user_name =: temp', temp = student_username)
    data = cursor.fetchone()

    email = data[0]
    name = data[1]
    bio = data[2]

    # Get all completed assignments
    cursor.execute("""SELECT ASSIGNMENT.ASSIGN_TITLE FROM STUDENT, ASSIGNMENT
                        WHERE ASSIGNMENT.STUDENT_GROUP =: student_group
                        AND STUDENT.PROGRESS > ASSIGNMENT.GAME_LEVEL
                        AND student.user_name =: username""", [student_group, student_username])
    complete_raw = cursor.fetchall()
    complete = []
    cursor.close()
    
    for assignment in complete_raw:
        complete.append(assignment[0])

    return jsonify({
        'username': student_username,
        'email': email,
        'name': name,
        'bio': bio,
        'assignments': complete
    })


@app.route("/dropStudent", methods=["GET", "POST"])
def dropStudent():
    data = request.get_json()
    student_username = data['username']
    cursor = conn.cursor()

    #Remove student from current student group
    cursor.execute('UPDATE student set student_group = null WHERE user_name =: temp', temp = student_username)
    conn.commit()
    cursor.close()

    return jsonify({})


app.secret_key = 'some other random key'

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)
    session['test'] = 10