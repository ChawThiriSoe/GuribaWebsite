from flask import Flask,render_template,request,session,redirect
from datetime import date
import sqlite3
import hashlib
import re
import os

app = Flask(__name__)
app.secret_key = 'Guriba'

def get_connection():
    con = sqlite3.connect('guribadb.db')
    con.row_factory = sqlite3.Row
    return con

@app.route('/')

# Userregister route
@app.route('/userregister', methods=['GET','POST'])
def user_register():
    if request.method == 'GET':
        return render_template('userregister.html')
    else:
        username = request.form['username']
        userdob = request.form['userdob']
        userpwd = request.form['userpwd']
        hashpwd = hashlib.sha256(userpwd.encode()).hexdigest()
        confirm_pwd = request.form['confirm_pwd']
        hashCpwd = hashlib.sha256(confirm_pwd.encode()).hexdigest()
        useremail = request.form['useremail']
        userimg = "static/images/defaultprofile.PNG"
        msg = ''
        condition_pwd = 0
        if hashpwd == hashCpwd:
            while True:
                if (len(userpwd)<8):
                    condition_pwd = -1
                    break
                elif not re.search('[a-z]', userpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[A-Z]', userpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[0-9]', userpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[!@#$%&_]', userpwd):
                    condition_pwd = -1
                    break
                elif re.search('\s', userpwd):
                    condition_pwd = -1
                    break
                else: 
                    condition_pwd = 0
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute('insert into useracc (username,userdob,userpwd,useremail,userimg) values (?,?,?,?,?)',(username,userdob,hashpwd,useremail,userimg))
                        conn.commit()
                        print('1')
                        return render_template('userlogin.html')

                    except sqlite3.Error as error:
                        msg = 'Failed to register.'
                        return render_template('userregister.html', msg = msg)
                    finally:
                        if conn:
                            cur.close()
                            conn.close()
                    break
            if condition_pwd == -1: 
                msg = 'Password is unstable.'
                return render_template('userregister.html', msg = msg, uname = username, dob = userdob, uemail = useremail)
        else:
            msg = 'Please enter password twice correctly.'
            return render_template('userregister.html', msg = msg, uname = username, dob = userdob, uemail = useremail)

# Userlogin route
@app.route('/userlogin', methods=['GET','POST'])
def user_login():
    if request.method == 'GET':
        return render_template('userlogin.html')
    else:
        uname = request.form['username']
        pwd = request.form['userpwd']
        hashpwd = hashlib.sha256(pwd.encode()).hexdigest()
        msg = ''
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from useracc where username = ? and userpwd = ?', (uname, hashpwd))
            rows = cur.fetchone()
            if rows:
                session['login'] = True
                session['userID'] = rows['userID']
                session['username'] = rows['username']
                session['userdob'] = rows['userdob']
                session['useremail'] = rows['useremail']
                session['userimg'] = rows['userimg']

                cur.execute('select storyID,storyimg,tagtype from story inner join tag on tag.tagID=story.tagID order by storyID limit 16')
                storydata = cur.fetchall()

                counter = 0
                allstorydata = []
                story1data = []
                for data in storydata:
                    if counter < 3:
                        story1data.append(data)
                        counter += 1
                    else:
                        counter = 0
                        story1data.append(data)
                        allstorydata.append(story1data)
                        story1data = []

                return render_template('userindex.html', allstorydata=allstorydata)
            else:
                msg = 'Can\'t find an account with that email and password.'
                return render_template('userlogin.html', msg = msg)
        except sqlite3.Error as error:
            msg = 'Try Again.'
            return render_template('userlogin.html', msg = msg)
        finally:
            if conn:
                cur.close()
                conn.close()

# Profile route
@app.route('/profile', methods=['POST'])
def profile():
    if 'userID' in session:
        userid = request.form['userid']
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.userID=?',(userid, ))
            storydata = cur.fetchall()

            cur.execute('select * from readinglist where userID=?',(userid, ))
            storylistdata = cur.fetchall()
            readinglistdata = []
            for data in storylistdata:
                cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.storyID=?',(data[1], ))
                story = cur.fetchall()
                readinglistdata.append((data,story))

            return render_template('otheruserprofile.html', userdata=userdata, storydata=storydata, totalstory=len(storydata), readinglistdata=readinglistdata, totallist=len(readinglistdata))
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Myprofile route
@app.route('/myprofile', methods=['GET'])
def myprofile():
    userid = session['userID']
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('select * from useracc where userID=?',(userid, ))
        userdata = cur.fetchone()

        cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.userID=?',(userid, ))
        storydata = cur.fetchall()

        cur.execute('select * from readinglist where userID=?',(userid, ))
        storylistdata = cur.fetchall()
        readinglistdata = []
        for data in storylistdata:
            cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.storyID=?',(data[1], ))
            story = cur.fetchall()
            readinglistdata.append((data,story))

        cur.execute('select * from library where userID=?',(userid, ))
        storylibrarydata = cur.fetchall()
        librarydata = []
        for data in storylibrarydata:
            cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.storyID=?',(data[1], ))
            story = cur.fetchall()
            librarydata.append((data,story))

        return render_template('myprofile.html', userdata=userdata, storydata=storydata, totalstory=len(storydata), readinglistdata=readinglistdata, totallist=len(readinglistdata), librarydata=librarydata, totallibrary=len(librarydata))
    except sqlite3.Error as error:
        return redirect('/userindex')
    finally:
        if conn:
            cur.close()
            conn.close()

# Editprofile route
@app.route('/editprofile', methods=['GET','POST'])
def editprofile():
    if request.method == 'GET':
        return render_template('editprofile.html')
    else:
        id = request.form['ppid']
        name = request.form['ppname']
        email = request.form['ppemail']
        img = request.files['ppimg']
        if img.filename != '':
            img.save(os.path.join('static/images/',img.filename))
            fpimg = os.path.join('static/images/',img.filename)
        else:
            fpimg = session['userimg'];
        msg=''
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('update useracc set username=?, useremail=?, userimg=? where userID=?',(name,email,fpimg,id))
            conn.commit()
            cur.execute('select * from useracc where userID=?', (id, ))
            rows = cur.fetchone()
            if rows:
                session['login'] = True
                session['userID'] = rows['userID']
                session['username'] = rows['username']
                session['userdob'] = rows['userdob']
                session['useremail'] = rows['useremail']
                session['userimg'] = rows['userimg']
                return render_template('myprofile.html')
            else:
                msg = 'Failed to Edit. Try Again.'
                return render_template('editprofile.html',msg=msg)
        except sqlite3.Error as error:
            msg = 'Failed to Edit. Try Again.'
            return render_template('editprofile.html',msg=msg)
        finally:
            if conn:
                cur.close()
                conn.close()

# Userindex route
@app.route('/userindex', methods=['GET'])
def userindex():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('select storyID,storyimg,tagtype from story inner join tag on tag.tagID=story.tagID order by storyID limit 16')
    storydata = cur.fetchall()

    counter = 0
    allstorydata = []
    story1data = []
    for data in storydata:
        if counter < 3:
            story1data.append(data)
            counter += 1
        else:
            counter = 0
            story1data.append(data)
            allstorydata.append(story1data)
            story1data = []

    return render_template('userindex.html', allstorydata=allstorydata)

# Storypreview route
@app.route('/storypreview', methods=['POST'])
def storypreview():
    if 'userID' in session:
        id = request.form['storyid']
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from story where storyID=?',(id, ))
            storydata = cur.fetchone()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            tagid = storydata['tagID']
            cur.execute('select * from tag where tagID=?',(tagid, ))
            tagdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?', (id, ))
            chapterdata = cur.fetchall()

            return render_template('storypreview.html', storydata=storydata, userdata=userdata, tagdata=tagdata, chapterdata=chapterdata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Storyreading route
@app.route('/storyreading', methods=['POST'])
def reading():
    if 'userID' in session:
        storyid = request.form['storyid']
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            chapterdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            allchapterdata = cur.fetchall()

            cur.execute('select userimg,username,commentID,comment from comment inner join useracc on useracc.userID=comment.userID where chapterID=?',(chapterdata[0], ))
            commentdata = cur.fetchall()
            return render_template('storyreading.html', storydata=storydata, userdata=userdata, chapterdata=chapterdata, commentdata=commentdata, allchapterdata=allchapterdata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Storyreadinglist route
@app.route('/storyreadinglist', methods=['POST'])
def readinglist():
    if 'userID' in session:
        chpid = request.form['chapterid']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from chapter where chapterID=?',(chpid, ))
            chapterdata = cur.fetchone()

            storyid = chapterdata['storyID']
            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            allchapterdata = cur.fetchall()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            cur.execute('select userimg,username,commentID,comment from comment inner join useracc on useracc.userID=comment.userID where chapterID=?',(chpid, ))
            commentdata = cur.fetchall()

            return render_template('storyreading.html', storydata=storydata, userdata=userdata, chapterdata=chapterdata, commentdata=commentdata, allchapterdata=allchapterdata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Comment route
@app.route('/comment', methods=['POST'])
def comment():
    if 'userID' in session:
        comment = request.form['comment']
        userid = request.form['userid']
        chapterid = request.form['chapterid']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('insert into comment (comment,userID,chapterID) values (?,?,?)',(comment,userid,chapterid))
            conn.commit()

            cur.execute('select * from chapter where chapterID=?',(chapterid, ))
            chapterdata = cur.fetchone()

            storyid = chapterdata['storyID']
            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            allchapterdata = cur.fetchall()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            cur.execute('select userimg,username,commentID,comment from comment inner join useracc on useracc.userID=comment.userID where chapterID=?',(chapterid, ))
            commentdata = cur.fetchall()

            return render_template('storyreading.html', storydata=storydata, userdata=userdata, chapterdata=chapterdata, commentdata=commentdata, allchapterdata=allchapterdata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Like route
@app.route('/like', methods=['POST'])
def like():
    if 'userID' in session:
        chapterid = request.form['chapterid']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from chapter where chapterID=?', (chapterid, ))
            storyid = cur.fetchone()[4]

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            if storydata['getlike'] == None:
                addlike = 1
            else:
                addlike = storydata['getlike'] + 1

            cur.execute('update story set getlike=? where storyID=?', (addlike,storyid))
            conn.commit()

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            chapterdata = cur.fetchone()
            return render_template('storyreading.html', storydata=storydata, userdata=userdata, chapterdata=chapterdata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Unlike route
@app.route('/unlike', methods=['POST'])
def unlike():
    if 'userID' in session:
        chapterid = request.form['chapterid']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from chapter where chapterID=?', (chapterid, ))
            storyid = cur.fetchone()[4]

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            if storydata['getunlike'] == None:
                addunlike = 1
            else:
                addunlike = storydata['getunlike'] + 1

            cur.execute('update story set getunlike=? where storyID=?', (addunlike,storyid))
            conn.commit()

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            chapterdata = cur.fetchone()
            return render_template('storyreading.html', storydata=storydata, userdata=userdata, chapterdata=chapterdata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Sharetofb route
@app.route('/sharetofb', methods=['POST'])
def sharetofb():
    if 'userID' in session:
        chapterid = request.form['chapterid']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from chapter where chapterID=?', (chapterid, ))
            storyid = cur.fetchone()[4]

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            if storydata['getsharing'] == None:
                addshare = 1
            else:
                addshare = storydata['getsharing'] + 1

            cur.execute('update story set getsharing=? where storyID=?', (addshare,storyid))
            conn.commit()

            return redirect('https://www.facebook.com/')
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Sharetoinsta route
@app.route('/sharetoinsta', methods=['POST'])
def sharetoinsta():
    if 'userID' in session:
        chapterid = request.form['chapterid']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from chapter where chapterID=?', (chapterid, ))
            storyid = cur.fetchone()[4]

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            if storydata['getsharing'] == None:
                addshare = 1
            else:
                addshare = storydata['getsharing'] + 1

            cur.execute('update story set getsharing=? where storyID=?', (addshare,storyid))
            conn.commit()

            return redirect('https://www.instagram.com/')
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Sharetotwt route
@app.route('/sharetotwt', methods=['POST'])
def sharetotwt():
    if 'userID' in session:
        chapterid = request.form['chapterid']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from chapter where chapterID=?', (chapterid, ))
            storyid = cur.fetchone()[4]

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            if storydata['getsharing'] == None:
                addshare = 1
            else:
                addshare = storydata['getsharing'] + 1

            cur.execute('update story set getsharing=? where storyID=?', (addshare,storyid))
            conn.commit()

            return redirect('https://twitter.com/?lang=en')
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Mystory route
@app.route('/mystory', methods=['GET'])
def mystory():
    if 'userID' in session:
        userid = session['userID']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from story where userID=?',(userid, ))
            storydata = cur.fetchall()

            allstorydata = []
            for data in storydata:
                cur.execute('select * from chapter where storyID=?',(data[0], ))
                chapter = cur.fetchall()
                allstorydata.append((data,chapter))

            return render_template('userstory.html', allstorydata=allstorydata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Introwriting route
@app.route('/introwriting', methods=['GET','POST'])
def introwriting():
    if 'userID' in session:
        if request.method == 'GET':
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from genre')
            genredata = cur.fetchall()
            return render_template('storywritingintro.html', genredata=genredata)
        else:
            img = request.files['coverimg']
            img.save(os.path.join('static/images/',img.filename))
            fpimg = os.path.join('static/images/',img.filename)

            title = request.form['title']
            intro = request.form['intro']
            tag = request.form['tag']
            genre = request.form['genre']
            userid = request.form['userid']

            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('select * from tag')
                findtag = cur.fetchall()
                tagdict = {}
                tagid = ''
                for line in findtag:
                    tagdict[line[0]] = line[1]

                if tag not in tagdict.values():
                    cur.execute('insert into tag (tagtype) values (?)', (tag, ))
                    conn.commit()
                    cur.execute('select * from tag where tagtype=?',(tag, ))
                    tags = cur.fetchone()
                    tagid = tags['tagID']
                else:
                    for id, type in tagdict.items():
                        if type == tag:
                            tagid = id
                            break

                cur.execute('insert into story (storytitle,storyintro,storyimg,genreID,tagID,userID) values (?,?,?,?,?,?)',(title,intro,fpimg,genre,tagid,userid))
                conn.commit()

                cur.execute('select * from story where storytitle=?', (title, ))
                storydata = cur.fetchone()
                return render_template('storywriting.html',storyid=storydata['storyID'])

            except sqlite3.Error as error:
                msg = 'Failed to create.'
                cur.execute('select * from genre')
                genredata = cur.fetchall()
                return render_template('storywritingintro.html', genredata=genredata, msg=msg)
            finally:
                if conn:
                    cur.close()
                    conn.close()
    else:
        return render_template('userlogin.html')

# Writingchapter route
@app.route('/writingchapter', methods=['POST'])
def writingchapter():
    if 'userID' in session:
        storyid = request.form['storyid']
        return render_template('storywriting.html',storyid=storyid)
    else:
        return render_template('userlogin.html')

# Chapterwriting route
@app.route('/chapterwriting', methods=['POST'])
def chapterwriting():
    if 'userID' in session:
        img = request.files['coverimg']
        img.save(os.path.join('static/images/',img.filename))
        fpimg = os.path.join('static/images/',img.filename)

        storyid = request.form['storyid']
        chptitle = request.form['chptitle']
        chppara = request.form['chppara']

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('insert into chapter (chaptertitle,chapterimg,chapterpara,storyID) values (?,?,?,?)', (chptitle,fpimg,chppara,storyid))
            conn.commit()

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()
            if storydata['totalchapter'] == None:
                totoalchp = 1
            else:
                totoalchp = storydata['totalchapter'] + 1
            today = date.today()
            cur.execute('update story set totalchapter=?,uploaddate=? where storyID=?',(totoalchp,today,storyid))
            conn.commit()

            cur.execute('select * from story where storyID=?', (storyid, ))
            storydata = cur.fetchone()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            chapterdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?',(storyid, ))
            allchapterdata = cur.fetchall()

            cur.execute('select * from comment where chapterID=?',(chapterdata[0], ))
            commentdata = cur.fetchall()
            return render_template('storyreading.html', storydata=storydata, userdata=userdata, chapterdata=chapterdata, commentdata=commentdata, allchapterdata=allchapterdata)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Contactus route
@app.route('/contactus', methods=['GET','POST'])
def contactus():
    if request.method == 'GET':
        return render_template('contactus.html')
    else:
        email = request.form['rpemail']
        topic = request.form['rptopic']
        message = request.form['rpmsg']
        check = 'Not Scrutinize'
        msg = ''
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('insert into report (reportemail,reporttopic,reportmsg, reportcheck) values (?,?,?,?)',(email,topic,message,check))
            conn.commit()
            msg = 'Thank you for your feedback. We\'ll check it.'
            return render_template('contactus.html', msg=msg)
        except sqlite3.Error as error:
            msg = 'Failed to sent. Please send again.'
            return render_template('contactus.html', msg = msg, email = email)
        finally:
            if conn:
                cur.close()
                conn.close()

# Addtolibrary route
@app.route('/addtolibrary', methods=['POST'])
def addtolibrary():
    if 'userID' in session:
        id = request.form['storyid']
        userid = request.form['userid']

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute('select * from library where userID=?', (userid, ))
            findlib = cur.fetchall()
            libdict = {}
            for line in findlib:
                libdict[str(line[2])]=str(line[1])

            if str(id) in libdict.values():
                msg = 'Already saved in your library.'
            else:
                cur.execute('insert into library (storyID,userID) values (?,?)', (id, userid))
                conn.commit()
                msg = 'Saved to your library.'

            cur.execute('select * from story where storyID=?',(id, ))
            storydata = cur.fetchone()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            tagid = storydata['tagID']
            cur.execute('select * from tag where tagID=?',(tagid, ))
            tagdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?', (id, ))
            chapterdata = cur.fetchall()

            return render_template('storypreview.html', storydata=storydata, userdata=userdata, tagdata=tagdata, chapterdata=chapterdata, msg=msg)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Addtoreadinglist route
@app.route('/addtoreadinglist', methods=['POST'])
def addtoreadinglist():
    if 'userID' in session:
        id = request.form['storyid']
        userid = request.form['userid']

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute('select * from readinglist where userID=?', (userid, ))
            findlib = cur.fetchall()
            libdict = {}
            for line in findlib:
                libdict[str(line[0])]=str(line[1])

            if str(id) in libdict.values():
                msg = 'Already saved in your reading list.'
            else:
                cur.execute('insert into readinglist (storyID,userID) values (?,?)', (id, userid))
                conn.commit()
                msg = 'Saved to your reading list.'

            cur.execute('select * from story where storyID=?',(id, ))
            storydata = cur.fetchone()

            userid = storydata['userID']
            cur.execute('select * from useracc where userID=?',(userid, ))
            userdata = cur.fetchone()

            tagid = storydata['tagID']
            cur.execute('select * from tag where tagID=?',(tagid, ))
            tagdata = cur.fetchone()

            cur.execute('select * from chapter where storyID=?', (id, ))
            chapterdata = cur.fetchall()

            return render_template('storypreview.html', storydata=storydata, userdata=userdata, tagdata=tagdata, chapterdata=chapterdata, msg=msg)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('userlogin.html')

# Search route
@app.route('/search', methods=['POST'])
def search():
    text = request.form['search']

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('select * from tag')
        tagdata = cur.fetchall()
        tagdict = {}
        matchtag = []
        for line in tagdata:
            tagdict[str(line[0])]=str(line[1])

        for tagid, tag in tagdict.items():
            match = re.search(text, tag, re.IGNORECASE)
            if match:
                matchtag.append(tagid)

        cur.execute('select * from genre')
        genredata = cur.fetchall()
        genredict = {}
        matchgenre = []
        for line in genredata:
            genredict[str(line[0])]=str(line[1])

        for genreid, genre in genredict.items():
            match = re.search(text, genre, re.IGNORECASE)
            if match:
                matchgenre.append(genreid)

        cur.execute('select * from story')
        storydata = cur.fetchall()
        storydict = {}
        matchstory = []
        for line in storydata:
            storydict[str(line['storyID'])]=str(line['storytitle'])

        for storyid, story in storydict.items():
            match = re.search(text, story, re.IGNORECASE)
            if match:
                matchstory.append(storyid)

        cur.execute('select * from useracc')
        userdata = cur.fetchall()
        userdict = {}
        matchuser = []
        for line in userdata:
            userdict[str(line['userID'])]=str(line['username'])

        for userid, user in userdict.items():
            match = re.search(text, user, re.IGNORECASE)
            if match:
                matchuser.append(userid)

        foundstorydata = {}
        if matchtag != []:
            for i in matchtag:
                cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.tagID=?',(i, ))
                story1 = cur.fetchall()
                for one in story1:
                    if one['storyID'] not in foundstorydata.keys():
                        foundstorydata[one['storyID']]=[]
                        foundstorydata[one['storyID']].append(one)

        if matchgenre != []:
            for i in matchgenre:
                cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.genreID=?',(i, ))
                story2 = cur.fetchall()
                for two in story2:
                    if two['storyID'] not in foundstorydata.keys():
                        foundstorydata[two['storyID']]=[]
                        foundstorydata[two['storyID']].append(two)

        if matchstory != []:
            for i in matchstory:
                cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.storyID=?',(i, ))
                story3 = cur.fetchall()
                for three in story3:
                    if three['storyID'] not in foundstorydata.keys():
                        foundstorydata[three['storyID']]=[]
                        foundstorydata[three['storyID']].append(three)

        matchstorydata = []
        for data in foundstorydata.values():
            matchstorydata.append(data)

        matchuserdata = ''
        if matchuser != []:
            for i in matchuser:
                cur.execute('select * from useracc where userID=?',(i, ))
                matchuserdata = cur.fetchall()
        return render_template('search.html', matchuserdata=matchuserdata, matchstorydata=matchstorydata, text=text, totalstory=len(matchstorydata), totaluser=len(matchuserdata))
    except sqlite3.Error as error:
        return redirect('/userindex')
    finally:
        if conn:
            cur.close()
            conn.close()

# Searchgenre route
@app.route('/searchgenre', methods=['POST'])
def searchgenre():
    name = request.form['genrename'].lower()

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('select * from genre where genretype=?',(name, ))
        genredata = cur.fetchone()
        genreid = genredata['genreID']

        cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.genreID=?',(genreid, ))
        storydata = cur.fetchall()
        return render_template('searchtag.html', storydata=storydata, totalstory=len(storydata), genrename=name)
    except sqlite3.Error as error:
        return redirect('/userindex')
    finally:
        if conn:
            cur.close()
            conn.close()

# Searchgtag route
@app.route('/searchtag', methods=['POST'])
def searchtag():
    name = request.form['tagname'].lower()

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('select * from tag where tagtype=?',(name, ))
        tagdata = cur.fetchone()
        tagid = tagdata['tagID']

        cur.execute('select storyID,storytitle,totalchapter,storyintro,storyimg,tagtype,genretype from story inner join tag on tag.tagID=story.tagID inner join genre on genre.genreID=story.genreID where story.tagID=?',(tagid, ))
        storydata = cur.fetchall()
        return render_template('searchtag.html', storydata=storydata, totalstory=len(storydata), genrename=name)
    except sqlite3.Error as error:
        return redirect('/userindex')
    finally:
        if conn:
            cur.close()
            conn.close()

# Term&condition route
@app.route('/term&condition')
def terms():
    return render_template('term&condition.html')

# Privacy route
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# Aboutus route
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

# Faq route
@app.route('/faq')
def faq():
    return render_template('faq.html')

# Forgetpwd route
@app.route('/forgetpwd', methods=['GET','POST'])
def forgetpwd():
    if request.method == 'GET':
        return render_template('forgetpwd.html')
    else:
        email = request.form['useremail']
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from useracc where useremail=?', (email, ))
            userdata = cur.fetchone()
            msg = ''
            if userdata:
                return render_template('changepwd.html', userdata=userdata)
            else:
                msg = 'There is no account with this email address.'
                return render_template('forgetpwd.html', msg=msg)
        except sqlite3.Error as error:
            return redirect('/userindex')
        finally:
            if conn:
                cur.close()
                conn.close()

# Chgpwd route
@app.route('/chgpwd', methods=['GET','POST'])
def chgpwd():
    if request.method == 'GET':
        return render_template('changepwd.html')
    else:
        id = request.form['userid']
        newpwd = request.form['userpwd']
        hashpwd = hashlib.sha256(newpwd.encode()).hexdigest()
        confirmnewpwd = request.form['confirmpwd']
        hashCpwd = hashlib.sha256(confirmnewpwd.encode()).hexdigest()
        msg = ''
        condition_pwd = 0
        if hashpwd == hashCpwd:
            while True:
                if (len(newpwd)<8):
                    condition_pwd = -1
                    break
                elif not re.search('[a-z]', newpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[A-Z]', newpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[0-9]', newpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[!@#$%&_]', newpwd):
                    condition_pwd = -1
                    break
                elif re.search('\s', newpwd):
                    condition_pwd = -1
                    break
                else: 
                    condition_pwd = 0
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute('update useracc set userpwd=? where userID=?',(hashpwd,id))
                        conn.commit()
                        return render_template('userlogin.html')

                    except sqlite3.Error as error:
                        msg = 'Failed to reset.'
                        return render_template('changepwd.html', msg = msg, id=id)
                    finally:
                        if conn:
                            cur.close()
                            conn.close()
                    break
            if condition_pwd == -1: 
                msg = 'Password is unstable.'
                return render_template('changepwd.html', msg = msg, id=id)
        else:
            msg = 'Please enter password twice correctly.'
            return render_template('changepwd.html', msg = msg, id=id)

# Userlogout route
@app.route('/userlogout')
def userlogout():
    session.pop('username',None)
    return render_template('userlogin.html')

# For Admin Side

# Adminregister route
@app.route('/adminregister', methods=['GET','POST'])
def admin_register():
    if request.method == 'GET':
        return render_template('adminregister.html')
    else:
        adminname = request.form['username']
        admindob = request.form['userdob']
        adminpwd = request.form['userpwd']
        hashpwd = hashlib.sha256(adminpwd.encode()).hexdigest()
        confirm_pwd = request.form['confirm_pwd']
        hashCpwd = hashlib.sha256(confirm_pwd.encode()).hexdigest()
        adminemail = request.form['useremail']
        msg = ''
        condition_pwd = 0
        if hashpwd == hashCpwd:
            while True:
                if (len(adminpwd)<8):
                    condition_pwd = -1
                    break
                elif not re.search('[a-z]', adminpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[A-Z]', adminpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[0-9]', adminpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[!@#$%&_]', adminpwd):
                    condition_pwd = -1
                    break
                elif re.search('\s', adminpwd):
                    condition_pwd = -1
                    break
                else: 
                    condition_pwd = 0
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute('insert into adminacc (adminname,admindob,adminpwd,adminemail) values (?,?,?,?)',(adminname,admindob,hashpwd,adminemail))
                        conn.commit()
                        return render_template('adminlogin.html')

                    except sqlite3.Error as error:
                        msg = 'Failed to register.'
                        return render_template('adminregister.html', msg = msg)
                    finally:
                        if conn:
                            cur.close()
                            conn.close()
                    break
            if condition_pwd == -1: 
                msg = 'Password is unstable.'
                return render_template('adminregister.html', msg = msg, uname = adminname, dob = admindob, uemail = adminemail)
        else:
            msg = 'Please enter password twice correctly.'
            return render_template('adminregister.html', msg = msg, uname = adminname, dob = admindob, uemail = adminemail)

# Adminlogin route
@app.route('/adminlogin', methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('adminlogin.html')
    else:
        uname = request.form['username']
        pwd = request.form['userpwd']
        hashpwd = hashlib.sha256(pwd.encode()).hexdigest()
        msg = ''
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from adminacc where adminname = ? and adminpwd = ?', (uname, hashpwd))
            rows = cur.fetchone()
            if rows:
                session['adminname'] = rows['adminname']
                session['adminid'] = rows['adminID']
                return render_template('adminindex.html')
            else:
                msg = 'Can\'t find an account with that email and password.'
                return render_template('adminlogin.html', msg = msg)
        except sqlite3.Error as error:
            msg = 'Try Again.'
            return render_template('adminlogin.html', msg = msg)
        finally:
            if conn:
                cur.close()
                conn.close()

# Adminindex route
@app.route('/adminindex')
def adminindex():
    return render_template('adminindex.html')

# Manageuser route
@app.route('/manageuser', methods=['GET','POST'])
def manageuser():
    if 'adminid' in session:
        if request.method == 'GET':
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('select * from useracc')
                userdata = cur.fetchall()
                return render_template('manageuser.html',userdata=userdata)
            except sqlite3.Error as error:
                return redirect('/adminindex')
            finally:
                if conn:
                    cur.close()
                    conn.close()
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                id = request.form['id']
                cur.execute('delete from useracc where userID=?',(id, ))
                conn.commit()
                cur.execute('select * from useracc')
                userdata = cur.fetchall()
                return render_template('manageuser.html',userdata=userdata)
            except sqlite3.Error as error:
                return redirect('/adminindex')
            finally:
                if conn:
                    cur.close()
                    conn.close()
    else:
        return render_template('adminlogin.html')

# Manageadmin route
@app.route('/manageadmin', methods=['GET','POST'])
def manageadmin():
    if 'adminid' in session:
        if request.method == 'GET':
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('select * from adminacc')
                admindata = cur.fetchall()
                return render_template('manageadmin.html',admindata=admindata)
            except sqlite3.Error as error:
                return redirect('/adminindex')
            finally:
                if conn:
                    cur.close()
                    conn.close()
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                id = request.form['id']
                cur.execute('delete from adminacc where adminID=?',(id, ))
                conn.commit()
                cur.execute('select * from adminacc')
                admindata = cur.fetchall()
                return render_template('manageadmin.html',admindata=admindata)
            except sqlite3.Error as error:
                return redirect('/adminindex')
            finally:
                if conn:
                    cur.close()
                    conn.close()
    else:
        return render_template('adminlogin.html')

# Managereport route
@app.route('/managereport', methods=['GET','POST'])
def managereport():
    if 'adminid' in session:
        if request.method == 'GET':
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('select * from report')
                reportdata = cur.fetchall()
                return render_template('managereport.html',reportdata=reportdata)
            except sqlite3.Error as error:
                return redirect('/adminindex')
            finally:
                if conn:
                    cur.close()
                    conn.close()
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                id = request.form['id']
                adminid = request.form['adminid']
                rpcheck = 'Scrutinized'
                cur.execute('update report set reportcheck=?, checkadminID=? where reportID=?',(rpcheck,adminid,id))
                conn.commit()
                cur.execute('select * from report')
                reportdata = cur.fetchall()
                return render_template('managereport.html',reportdata=reportdata)
            except sqlite3.Error as error:
                return redirect('/adminindex')
            finally:
                if conn:
                    cur.close()
                    conn.close()
    else:
        return render_template('adminlogin.html')

# Managestory route
@app.route('/managestory', methods=['GET'])
def managestory():
    if 'adminid' in session:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from story')
            storydata = cur.fetchall()

            allstorydata = []
            for data in storydata:
                cur.execute('select * from chapter where storyID=?',(data[0], ))
                chapter = cur.fetchall()
                allstorydata.append((data,chapter))
            return render_template('managestory.html', allstorydata=allstorydata)
        except sqlite3.Error as error:
            return redirect('/adminindex')
        finally:
            if conn:
                cur.close()
                conn.close()
    else:
        return render_template('adminlogin.html')

# Deletestory route
@app.route('/deletestory', methods=['POST'])
def deletestory():
    storyid = request.form['storyid']
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('delete from story where storyID=?',(storyid, ))
        conn.commit()

        cur.execute('delete from chapter where storyID=?',(storyid, ))
        conn.commit()

        cur.execute('select * from story')
        storydata = cur.fetchall()

        allstorydata = []
        for data in storydata:
            cur.execute('select * from chapter where storyID=?',(data[0], ))
            chapter = cur.fetchall()
            allstorydata.append((data,chapter))
        return render_template('managestory.html', allstorydata=allstorydata)
    except sqlite3.Error as error:
        return redirect('/adminindex')
    finally:
        if conn:
            cur.close()
            conn.close()

# Deletechapter route
@app.route('/deletechapter', methods=['POST'])
def deletechapter():
    chapterid = request.form['chapterid']

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('delete from chapter where chapterID=?',(chapterid, ))
        conn.commit()

        cur.execute('select * from story')
        storydata = cur.fetchall()

        allstorydata = []
        for data in storydata:
            cur.execute('select * from chapter where storyID=?',(data[0], ))
            chapter = cur.fetchall()
            allstorydata.append((data,chapter))
        return render_template('managestory.html', allstorydata=allstorydata)
    except sqlite3.Error as error:
        return redirect('/adminindex')
    finally:
        if conn:
            cur.close()
            conn.close()

# Adminlogout route
@app.route('/adminlogout')
def adminlogout():
    session.pop('adminname',None)
    return render_template('adminlogin.html')

# Adminforgetpwd route
@app.route('/adminforgetpwd', methods=['GET','POST'])
def adminforgetpwd():
    if request.method == 'GET':
        return render_template('adminforgetpwd.html')
    else:
        email = request.form['adminemail']
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('select * from adminacc where adminemail=?', (email, ))
            admindata = cur.fetchone()
            msg = ''
            if admindata:
                return render_template('adminchangepwd.html', admindata=admindata)
            else:
                msg = 'There is no account with this email address.'
                return render_template('adminforgetpwd.html', msg=msg)
        except sqlite3.Error as error:
            msg = 'Try Again.'
            return render_template('adminforgetpwd.html', msg=msg)
        finally:
            if conn:
                cur.close()
                conn.close()

# Adminchgpwd route
@app.route('/adminchgpwd', methods=['GET','POST'])
def adminchgpwd():
    if request.method == 'GET':
        return render_template('adminchangepwd.html')
    else:
        id = request.form['adminid']
        newpwd = request.form['adminpwd']
        hashpwd = hashlib.sha256(newpwd.encode()).hexdigest()
        confirmnewpwd = request.form['confirmpwd']
        hashCpwd = hashlib.sha256(confirmnewpwd.encode()).hexdigest()
        msg = ''
        condition_pwd = 0
        if hashpwd == hashCpwd:
            while True:
                if (len(newpwd)<8):
                    condition_pwd = -1
                    break
                elif not re.search('[a-z]', newpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[A-Z]', newpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[0-9]', newpwd):
                    condition_pwd = -1
                    break
                elif not re.search('[!@#$%&_]', newpwd):
                    condition_pwd = -1
                    break
                elif re.search('\s', newpwd):
                    condition_pwd = -1
                    break
                else: 
                    condition_pwd = 0
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute('update adminacc set adminpwd=? where adminID=?',(hashpwd,id))
                        conn.commit()
                        return render_template('adminlogin.html')

                    except sqlite3.Error as error:
                        msg = 'Failed to reset.'
                        return render_template('adminchangepwd.html', msg = msg, id=id)
                    finally:
                        if conn:
                            cur.close()
                            conn.close()
                    break
            if condition_pwd == -1: 
                msg = 'Password is unstable.'
                return render_template('adminchangepwd.html', msg = msg, id=id)
        else:
            msg = 'Please enter password twice correctly.'
            return render_template('adminchangepwd.html', msg = msg, id=id)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5779, debug=True)