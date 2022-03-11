from flask import Flask
from flask import render_template
from flask import request
from flask import session
import datetime
from flask import redirect, url_for

from flask_pymongo import PyMongo
# from flask_mail import * 

app = Flask(__name__) 
app.secret_key = "Atreyee"


#Flask mail configuration  
app.config['MAIL_SERVER']='smtp.gmail.com'  
app.config['MAIL_PORT']=465  
app.config['MAIL_USERNAME'] = 'atreyeemallick14@gmail.com'  
app.config['MAIL_PASSWORD'] = 'Atreyee14@'  
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_USE_SSL'] = True  
  
#instantiate the Mail class  
# mail = Mail(app)  


# mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/project_env")
mongodb_client = PyMongo(app, uri="mongodb+srv://Sayanh2:sayan123@cluster0.vb2op.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

# mongodb_client = PyMongo(app, uri="mongodb+srv://Atreyee123:atreyee123@cluster0.hxukg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# mongodb+srv://Sayanh2:sayan123@cluster0.vb2op.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
db = mongodb_client.db



# ****************** HOME ******************

@app.route('/')  
def homePage():  
    return render_template('home.html')



# ****************** STUDENT  BIO ******************

@app.route('/userReg', methods=["GET", "POST"])  
def userReg():
    if request.method == 'GET':
        return render_template('userReg.html')

    else:
        studentReg = db.usercollection.find_one({'useremail': request.form['email']})
        if studentReg:
            return render_template('userReg.html', failureMsg = "You have already registered with this Email ID")
        else:
            x = datetime.datetime.now()
            x = '' + str(x)
            db.usercollection.insert_one(
            {'username': request.form['fullName'],
            'useremail': request.form['email'],
            'usermobile': request.form['mobileNo'],
            'usercountry': request.form['country'],
            'usergender': request.form['gender'],
            'userdob': request.form['DOB'],
            'userpass': request.form['pass'],
            'useraddress': request.form['address'],
            'userdate': x
            })

            # msg = Message('Registration Successfull', sender = 'atreyeemallick14@gmail.com', recipients=[request.form['email']])  
            # s = 'Your Password is: ' + request.form['pass'] + ' Your Mobile No is: ' + request.form['mobileNo']
            # msg.body = 'Thank You , For your registration...Registration Successfull ' + s
            # mail.send(msg)

            return render_template('userReg.html', successMsg = "You have successfully registered")


@app.route('/userLogin', methods=["GET", "POST"])  
def userLogin(): 
    if request.method == 'GET': 
        return render_template('userLogin.html')
    else:
        user = db.usercollection.find_one(
        {'useremail': request.form['email'],
         'userpass': request.form['pass']
        })
        # print(user)
        userDetails = db.studentDetails.find_one({
            'studentEmail': request.form['email']
        })
        # print(userDetails)
        
        if user:
            session['uemail']= user['useremail']
            session['uname'] = user['username']
            session['usertype']= 'USER'
            print(userDetails)
            # studentDetails = db.studentDetails.find_one({'studentEmail': request.form['email']})
            # if userDetails:
            #     return render_template('userAfterLogin.html', userObj = user, userDetailsObj = userDetails, userName = session['uname'], search_result = 1)
            # else:
            # return render_template('userAfterLogin.html', userObj = user, userDetailsObj = userDetails, userName = session['uname'], userDetailsObjTrue = 1)
            return redirect(url_for('userAfterLogin'))
        else:
            return render_template('userLogin.html', errormsg = "INVALID UID OR PASSWORD")


@app.route('/userAfterLogin')
def userAfterLogin():
    user = db.usercollection.find_one({'useremail': session['uemail']})
    userDetails = db.studentDetails.find({'studentEmail': session['uemail']})

    if userDetails:
        return render_template('userAfterLogin.html', userObj = user, userDetailsObj = userDetails, userName = session['uname'], userDetailsObjTrue = 1)    
    else:
        return render_template('userAfterLogin.html', userObj = user, userDetailsObj = userDetails, userName = session['uname'])



@app.route('/updateUserProfile', methods=["GET", "POST"])  
def updateUserProfile():
    if request.method == 'GET':
        uemail = session['uemail']      
        userobj = db.usercollection.find_one({'useremail': uemail})
        return render_template('updateUserProfile.html', userdata = userobj)
    else:
        db.usercollection.update_one( {'useremail': session['uemail'] },
        { "$set": { 'username': request.form['fullName'],
                    'usermobile': request.form['mobileNo'],
                    'userpass': request.form['pass'],
                    'useraddress': request.form['address'] 
                  } 
        })
        return redirect(url_for('userAfterLogin'))



@app.route('/contactMentor', methods=["GET", "POST"])
def contactMentor():
    if request.method == 'GET':
        return render_template('contactMentor.html', userName = session['uname'])
    else:
        studentMentor = db.studentDetails.find_one({'studentMentorName': request.form['mentorName'], 'studentName': request.form['name']})
        if studentMentor:
            x = datetime.datetime.now()
            x = '' + str(x)
            db.contactMentor.insert_one(
            {'studentName': request.form['name'],
            'studentRoll': request.form['roll'],
            'studentMentorName': request.form['mentorName'],
            'studentQueryTopic': request.form['queryTopic'],
            'studentQuery': request.form['query'],
            'queryDate': x
            })
            return render_template('contactMentor.html', successMsg = 'Your query has been sended successfully', userName = session['uname'])
        else:
            return render_template('contactMentor.html', failureMsg = 'Sorry, You do not have any Mentor', userName = session['uname'])





# ****************** LOG OUT ******************

@app.route('/logout')  
def logout():  
    if 'usertype' in session:
        utype = session['usertype']
        if utype == 'ADMIN':
            session.pop('usertype',None)
        elif utype == 'TEACHER':
            session.pop('usertype', None)
            session.pop('uemail',None)
            session.pop('uname',None)
        else: 
            session.pop('usertype',None)
            session.pop('uemail',None)
            session.pop('uname',None)
        return redirect(url_for('homePage'));    
    else:  
        return '<p>user already logged out</p>' 





# ****************** STUDENT DETAILS ******************

@app.route('/studentDetails', methods=["GET", "POST"])
def studentDetails():
    # user = db.usercollection.find_one({'useremail': session['uemail']})
    # userDetails = db.studentDetails.find_one({'studentEmail': session['uemail']})
    if request.method == 'GET':
        # studentDetails = db.studentDetails.find_one({'useremail': session['uemail']})
        # if studentDetails:
        #     return render_template('userAfterLogin.html', userName = session['uname'], userObj = user, userDetailsObj = userDetails, failureMsg = 'You Have already Added your details')
        # else:
        return render_template('studentDetails.html')
    else:
        x = datetime.datetime.now()
        x = '' + str(x)
        # print(userDetails)
        db.studentDetails.insert_one({
            'studentName': request.form['name'],
            'studentEmail': request.form['email'],
            'studentRoll': request.form['roll'],
            'studentDept': request.form['dept'],
            'studentSem': request.form['sem'],
            'studentSession': request.form['session'],
            'studentCGPA': 'NA',
            'studentNewTech': 'NA',
            'studentCertificates': 'NA',
            'studentMentorName': 'NA',
            'studentMentorEmail': 'NA',
            'studentMentorScore': 'NA',
            'studentMetorRemarks': 'NA',
            'studentDate': x
            })
        # return render_template('userAfterLogin.html', userName = session['uname'], userObj = user, userDetailsObj = userDetails, successMsg = "Your Details have been updated Successfully")
        return redirect(url_for('userAfterLogin'))






# ****************** TEACHER ******************

@app.route('/teacherReg', methods=["GET", "POST"])
def teacherReg():
    if request.method == 'GET':
        return render_template('teacherReg.html')
    else:
        db.teacherCollection.insert_one(
        {'teacherName': request.form['fullName'],
        'teacherDept' : request.form['dept'],
        'teacherEmail': request.form['email'],
        'teacherMobile': request.form['mobileNo'],
        'teacherCountry': request.form['country'],
        'teacherGender': request.form['gender'],
        'teacherDOB': request.form['DOB'],
        'teacherPass': request.form['pass'],
        'teacherAddress': request.form['address'],
        })
        return render_template('teacherReg.html', successMsg = "You have successfully registered")



@app.route('/teacherLogin', methods = ['GET', 'POST'])
def teacherLogin():
    if request.method == 'GET':
        return render_template('teacherLogin.html')
    else:
        teacher = db.teacherCollection.find_one({
            'teacherEmail': request.form['email'],
            'teacherPass': request.form['pass']
        })
    
    userObj = db.usercollection.find({})
    # studentDetails = db.studentDetails.find({})

    if teacher:
        session['uemail']= teacher['teacherEmail']
        session['uname'] = teacher['teacherName']
        session['usertype']= 'TEACHER'
        studentDetails = db.studentDetails.find({'studentMentorEmail': session['uemail']})
        if studentDetails:
            return render_template('teacherAfterLogin.html', teacherName = session['uname'], userData = userObj, studentDetailsObj = studentDetails, search_result = 1)
        else:
            return render_template('teacherAfterLogin.html', teacherName = session['uname'], userData = userObj, studentDetailsObj = studentDetails)

    else:
        return render_template('teacherLogin.html', errormsg = "INVALID UID OR PASSWORD")



@app.route('/teacherAfterLogin', methods = ['GET', 'POST'])
def teacherAfterLogin():
    userObj = db.usercollection.find({})
    studentDetails = db.studentDetails.find({'studentMentorEmail': session['uemail']})
    print(session['uemail'])
    if studentDetails:
        return render_template('teacherAfterLogin.html', teacherName = session['uname'], userData = userObj, studentDetailsObj = studentDetails, search_result = 1)
    else:
        return render_template('teacherAfterLogin.html', teacherName = session['uname'], userData = userObj, studentDetailsObj = studentDetails)


@app.route('/updateStudentByTeacher', methods = ['GET', 'POST'])
def updateStudentByTeacher():

    if request.method == 'GET':
        studentData = db.studentDetails.find_one({'studentEmail': request.args.get('email'), 'studentSem': request.args.get('sem')})
        print(studentData)
        return render_template('updateStudentByTeacher.html', studentObj = studentData)
    else:
        db.studentDetails.update_one({'studentSem': request.form['sem']},
        { "$set": { 'studentCGPA': request.form['CGPA'],
                    'studentNewTech': request.form['newTech'],
                    'studentCertificates': request.form['certificates'],
                    'studentMentorScore': request.form['mentorScore'], 
                    'studentMetorRemarks': request.form['mentorRemarks'] 
                  } 
        })
        return redirect(url_for('teacherAfterLogin'))


@app.route('/studentQuery', methods = ['GET', 'POST'])
def studentQuery():
    studentQuery = db.contactMentor.find({'studentMentorName': session['uname']})
    if studentQuery is not None:
        return render_template('studentQuery.html', studentQueryObj = studentQuery, queryTrue = 1, teacherName = session['uname'])
    elif studentQuery is None:
        return render_template('studentQuery.html', queryMsg = 'You have no queries from your students', queryFalse = 1, teacherName = session['uname'])



@app.route('/studentHistory', methods = ['GET', 'POST'])
def studentHistory():
    teacherName = session['uname']
    if request.method == 'GET':
        return render_template('studentHistory.html', teacherName = teacherName)
    else:
        studentDetails = db.studentDetails.find({'studentRoll': request.form['roll']})
        if studentDetails:
            return render_template('studentHistory.html', studentDetailsObj = studentDetails, searchStudent = 1, teacherName = teacherName)
        else:
             return render_template('studentHistory.html', failureMsg = 'This Roll No does not exist', teacherName = teacherName)
    






# ****************** ADMIN ******************

@app.route('/adminLogin', methods=['GET','POST'])  
def adminLogin(): 
    if request.method == 'GET':
        return render_template('adminLogin.html')
    else:      
        adminId = request.form['adminId']
        adminPass = request.form['adminPass']

        teacherCSE = db.teacherCollection.find({'teacherDept': 'CSE'})
        teacherIT = db.teacherCollection.find({'teacherDept': 'IT'})
        teacherMechanical = db.teacherCollection.find({'teacherDept': 'Mechanical'})
        teacherCivil = db.teacherCollection.find({'teacherDept': 'Civil'})

        if(adminId == 'admin' and adminPass == 'Atreyee1@'):
            session['usertype']= 'ADMIN'
            return render_template('adminAfterLogin.html', teacherCSEObj = teacherCSE, teacherITObj = teacherIT, teacherMechanicalObj = teacherMechanical, teacherCivilObj = teacherCivil)
        else:
            return render_template('adminLogin.html', msg = 'INVALID UID OR PASS')


@app.route('/adminHome')  
def adminHome(): 
    teacherCollection = db.teacherCollection.find({})
    teacherCSE = db.teacherCollection.find({'teacherDept': 'CSE'})
    teacherIT = db.teacherCollection.find({'teacherDept': 'IT'})
    teacherMechanical = db.teacherCollection.find({'teacherDept': 'Mechanical'})
    teacherCivil = db.teacherCollection.find({'teacherDept': 'Civil'})
    return render_template('adminAfterLogin.html', teacherCollectionData = teacherCollection, teacherCSEObj = teacherCSE, teacherITObj = teacherIT, teacherMechanicalObj = teacherMechanical, teacherCivilObj = teacherCivil)



@app.route('/searchTeacher', methods=['GET','POST'])
def searchTeacher():
    teacherCollection = db.teacherCollection.find({})
    teacherCSE = db.teacherCollection.find({'teacherDept': 'CSE'})
    teacherIT = db.teacherCollection.find({'teacherDept': 'IT'})
    teacherMechanical = db.teacherCollection.find({'teacherDept': 'Mechanical'})
    teacherCivil = db.teacherCollection.find({'teacherDept': 'Civil'})
    if request.method == 'GET':
        return render_template('adminAfterLogin.html', teacherCollectionData = teacherCollection)
    else:
        searchResult = db.teacherCollection.find_one({'teacherName': request.form['teacherName']})
        # print(searchResult)
        
        if searchResult:
            return render_template('adminAfterLogin.html', teacherCSEObj = teacherCSE, teacherITObj = teacherIT, teacherMechanicalObj = teacherMechanical, teacherCivilObj = teacherCivil, searchTeacher = 1, searchResultObj = searchResult)
        else:
            return render_template('adminAfterLogin.html', searchTeacherFalse = 1, searchTeacherFalseMsg = 'No Teacher available of this Name', teacherCSEObj = teacherCSE, teacherITObj = teacherIT, teacherMechanicalObj = teacherMechanical, teacherCivilObj = teacherCivil, searchTeacher = 1, searchResultObj = searchResult) 




# @app.route('/studentDelete', methods=['GET','POST'])
# def studentDelete():
#     if request.method == 'GET':
#         return render_template('studentDelete.html')
#     else:
#         studentDataDelete = db.usercollection.find_one_and_delete({
#             'username': request.form['fullName']
#         })
#         if studentDataDelete is not None:
#             return render_template('studentDelete.html', msg = 'Student has been Deleted')
#         else:
#             return render_template('studentDelete.html', msg = 'This name is not available')



@app.route('/assignMentor', methods=['GET','POST'])
def assignMentor():
    if request.method == 'GET':
        return render_template('assignMentor.html')
    else:
        studentRoll = db.studentDetails.find_one({'studentRoll': request.form['roll'], 'studentSem': request.form['sem']})
        if studentRoll:
            db.studentDetails.update_one( {'studentRoll': request.form['roll'], 'studentSem': request.form['sem']},
            { "$set": { 
                        'studentMentorName': request.form['mentorName'], 
                        'studentMentorEmail': request.form['mentorEmail'] 
                    } 
            })
            return render_template('assignMentor.html', successMsg = 'Mentor has been successfully assigned')
        else:
            return render_template('assignMentor.html', failureMsg = 'You have Entered Wrong Roll No')





@app.route('/deleteTeacher', methods=['POST'])  
def deleteTeacher():
    print(request.form['email']) 
    responsefrommongodb = db.teacherCollection.find_one_and_delete({'teacherEmail': request.form['email']})
    print(responsefrommongodb)
    return redirect(url_for('adminHome'))




@app.route('/viewAll')  
def viewAll(): 
    studentCSE = db.studentDetails.find({'studentDept': 'CSE'})
    studentIT = db.studentDetails.find({'studentDept': 'IT'})
    studentECE = db.studentDetails.find({'studentDept': 'ECE'})
    studentCivil = db.studentDetails.find({'studentDept': 'Civil'})
    print(studentCSE)
    return render_template('viewAllAdmin.html', studentCSEObj = studentCSE, studentITObj = studentIT, studentECEObj = studentECE, studentCivilObj = studentCivil)



@app.route('/searchStudent', methods=['GET','POST'])
def searchStudent():
    studentCSE = db.studentDetails.find({'studentDept': 'CSE'})
    studentIT = db.studentDetails.find({'studentDept': 'IT'})
    studentECE = db.studentDetails.find({'studentDept': 'ECE'})
    studentCivil = db.studentDetails.find({'studentDept': 'Civil'})
    studentDetails = db.studentDetails.find({})
    if request.method == 'GET':
        return render_template('viewAllAdmin.html', studentDetailsObj = studentDetails)
    else:
        searchResult = db.studentDetails.find_one({'studentRoll': request.form['studentRoll']})
        # print(searchResult)
        if searchResult:
            return render_template('viewAllAdmin.html', searchStudent = 1, searchResultObj = searchResult,  studentCSEObj = studentCSE, studentITObj = studentIT, studentECEObj = studentECE, studentCivilObj = studentCivil)
        else:
            return render_template('viewAllAdmin.html', studentCSEObj = studentCSE, studentITObj = studentIT, studentECEObj = studentECE, studentCivilObj = studentCivil, searchStudentFalse = 1, searchStudentFalseMsg = 'No Student available of this Name') 



@app.route('/deleteStudent', methods=['POST'])  
def deleteStudent():
    print(request.form['email']) 
    responsefrommongodb = db.studentDetails.find_one_and_delete({'studentEmail': request.form['email']})
    print(responsefrommongodb)
    return redirect(url_for('viewAll'))



@app.route('/studentQueryAdmin', methods=['POST'])
def studentQueryAdmin():
    x = datetime.datetime.now()
    x = '' + str(x)
    db.contactAdmin.insert_one({
        'studentName': request.form['name'],
        'studentEmail': request.form['email'],
        'querySubject': request.form['subject'],
        'queryMessage': request.form['message'],
        'queryDate': x
    })
    return render_template('home.html', successMsg = 'Your Query has been sended successfully')



@app.route('/viewStudentQueryAdmin', methods = ['GET'])
def viewStudentQueryAdmin():
    studentQuery = db.contactAdmin.find({})
    print(studentQuery)
    if studentQuery:
        return render_template('studentQueryAdmin.html', studentQueryObj = studentQuery, queryTrue = 1)
    elif studentQuery:
        return render_template('studentQueryAdmin.html', queryMsg = 'You have no queries from your students', queryFalse = 1)





if __name__ =='__main__':  
    app.run(debug = True) 






#     @app.route('/studentDetails', methods=["GET", "POST"])
# def studentDetails():
#     user = db.usercollection.find_one({'useremail': session['uemail']})
#     userDetails = db.studentDetails.find_one({'studentEmail': session['uemail']})
#     if request.method == 'GET':
#         studentDetails = db.studentDetails.find_one({'useremail': session['uemail']})
#         if studentDetails:
#             return render_template('userAfterLogin.html', userName = session['uname'], userObj = user, userDetailsObj = userDetails, failureMsg = 'You Have already Added your details')
#         else:
#             return render_template('studentDetails.html')
#     else:
#         x = datetime.datetime.now()
#         x = '' + str(x)
#         print(userDetails)
#         db.studentDetails.insert_one({
#             'studentName': request.form['name'],
#             'studentEmail': request.form['email'],
#             'studentRoll': request.form['roll'],
#             'studentDept': request.form['dept'],
#             'studentSem': request.form['sem'],
#             'studentSession': request.form['session'],
#             'studentCGPA': 'NA',
#             'studentNewTech': 'NA',
#             'studentCertificates': 'NA',
#             'studentMentorName': 'NA',
#             'studentMentorEmail': 'NA',
#             'studentMentorScore': 'NA',
#             'studentMetorRemarks': 'NA',
#             'studentDate': x
#             })
#         return render_template('userAfterLogin.html', userName = session['uname'], userObj = user, userDetailsObj = userDetails, successMsg = "Your Details have been updated Successfully")


# @app.route('/userAfterLogin')
# def userAfterLogin():
#     user = db.usercollection.find_one({'useremail': session['uemail']})
#     userDetails = db.studentDetails.find_one({'studentEmail': session['uemail']})
    
#     return render_template('userAfterLogin.html', userObj = user, userDetailsObj = userDetails, userName = session['uname'])



# @app.route('/studentQuery', methods = ['GET', 'POST'])
# def studentQuery():
#     studentQuery = db.contactMentor.find({'studentMentorName': session['uname']})
#     if studentQuery:
#         return render_template('studentQuery.html', studentQueryObj = studentQuery, query = 1, teacherName = session['uname'])
#     else:
#         return render_template('studentQuery.html', queryMsg = 'You have no queries from your students', noQuery = 1, teacherName = session['uname'])




# @app.route('/studentDetails', methods=["GET", "POST"])
# def studentDetails():
#     user = db.usercollection.find_one({'useremail': session['uemail']})
#     userDetails = db.studentDetails.find_one({'studentEmail': session['uemail']})
#     if request.method == 'GET':
#         studentDetails = db.studentDetails.find_one({'useremail': session['uemail']})
#         if studentDetails:
#             return render_template('userAfterLogin.html', userName = session['uname'], userObj = user, userDetailsObj = userDetails, failureMsg = 'You Have already Added your details')
#         else:
#             return render_template('studentDetails.html')
#     else:
#         x = datetime.datetime.now()
#         x = '' + str(x)
#         print(userDetails)
#         db.studentDetails.insert_one({
#             'studentName': request.form['name'],
#             'studentEmail': request.form['email'],
#             'studentRoll': request.form['roll'],
#             'studentDept': request.form['dept'],
#             'studentSem': request.form['sem'],
#             'studentSession': request.form['session'],
#             'studentCGPA': 'NA',
#             'studentNewTech': 'NA',
#             'studentCertificates': 'NA',
#             'studentMentorName': 'NA',
#             'studentMentorEmail': 'NA',
#             'studentMentorScore': 'NA',
#             'studentMetorRemarks': 'NA',
#             'studentDate': x
#             })
#         # return render_template('userAfterLogin.html', userName = session['uname'], userObj = user, userDetailsObj = userDetails, successMsg = "Your Details have been updated Successfully")
#         return redirect(url_for('userAfterLogin'))