from flask import Flask, flash, redirect, request, render_template, jsonify
from db_helper import connect
import pandas as pd
import re
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
application = app

IMAGE_FOLDER = os.path.join('static', 'img')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER


@app.route("/")
def main():
    flash('Welcome')
    return render_template('index.html')
    
@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/result",methods=['POST'])
def result():
    sent = request.form['input_user']
    sent = sent.lower()
    sent = re.sub(r'[^a-z]', ' ', sent)
    tokens = sent.split()

    list_traits = ['Aggreeableness', 'Conscientiousness', 'Extraversion', 'Neuroticism', 'Openness']
    list_freq = [0, 0, 0, 0, 0]
    i = 0

    db = connect()
    res_table = []

    while i < len(tokens):
        temp = []
        temp_traits = []
        temp_subtraits = []
        cur = db.cursor()
        cur.execute("SELECT * FROM ontologi WHERE words like '%" + tokens[i] + "%'")
        for row in cur.fetchall():
            temp.append(row[1])
            temp_traits.append(row[2])
            temp_subtraits.append(row[3])
        maks = 0
        trait = ''
        subtrait = ''
        words = ''
        cur.close()
        for k in range(len(temp)):
            if re.sub('_', ' ', temp[k].lower()) in sent:
                if len(temp[k].split('_')) > maks:
                    words = temp[k].split('_')
                    trait = temp_traits[k]
                    subtrait = temp_subtraits[k]
                    maks = len(temp[k].split('_'))
        if maks > 0:
            res_table.append([' '.join(words), trait, subtrait])
            list_freq[list_traits.index(trait)] += 1
            i += maks
        else:
            i += 1

    db.close()

    return render_template('result.html', trait = list_traits, freq = list_freq, table_traits = res_table,len = len(list_freq))

@app.route("/list_new_traits", methods=['GET'])
def get_list_new_traits():
    db = connect()
    cur = db.cursor()
    res = []
    cur.execute("SELECT * FROM ontologi_vote")
    for row in cur.fetchall():
        res.append(row)
    cur.close()
    db.close()
    return render_template('list_new_traits.html', traits = res)

@app.route("/list_all_traits", methods=['GET'])
def get_list_all_traits():
    db = connect()
    cur = db.cursor()
    res = []
    cur.execute("SELECT * FROM ontologi")
    for row in cur.fetchall():
        res.append(row)
    cur.close()
    db.close()
    return render_template('list_all_traits.html', traits = res)

@app.route("/add_trait", methods=['POST', 'GET'])
def add_trait():
    words = request.form['words']
    traits = request.form['traits']
    if words != '' and traits != '':
        words_clean = re.sub(r'[^a-z]', ' ', words.lower())
        words_clean_fix = '_'.join(words_clean.split())
        db = connect()
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM ontologi_vote WHERE texts = '{}'".format(words_clean_fix))
        words_counts = cur.fetchone()[0]
        cur.close()
        if words_counts == 0:
            cur = db.cursor()
            cur.execute("INSERT INTO ontologi_vote (texts, traits, upvote, downvote) VALUES ('{}', '{}', '0', '0')".format(words_clean_fix, traits))
            db.commit()
            cur.close()
            db.close()
        else:
            print('Kata sudah ada')
    
    return redirect('list_new_traits')

@app.route("/upvote", methods=['POST'])
def upvote():
    texts = request.form['texts']
    db = connect()
    cur = db.cursor()
    cur.execute("UPDATE ontologi_vote \
        SET upvote = upvote + 1 \
        WHERE texts = '{}';".format(texts))
    db.commit()
    cur.close()
    db.close()
    return get_list_new_traits()

@app.route("/downvote", methods=['POST'])
def downvote():
    texts = request.form['texts']
    db = connect()
    cur = db.cursor()
    cur.execute("UPDATE ontologi_vote \
        SET downvote = downvote + 1 \
        WHERE texts = '{}';".format(texts))
    db.commit()
    cur.close()
    db.close()
    return get_list_new_traits()

@app.route("/set_trait")
def set_trait():
    return render_template('add_new_traits.html')

@app.route("/view_submit_traits")
def view_submit_traits():
    db = connect()
    cur = db.cursor()
    res = []
    cur.execute("SELECT * FROM ontologi_vote")
    for row in cur.fetchall():
        res.append(row)
    cur.close()
    db.close()
    return render_template('view_submit_traits.html', traits = res)

@app.route("/view_delete_traits")
def view_delete_traits():
    db = connect()
    cur = db.cursor()
    res = []
    cur.execute("SELECT * FROM ontologi_vote")
    for row in cur.fetchall():
        res.append(row)
    cur.close()
    db.close()
    return render_template('view_delete_traits.html', traits = res)

@app.route("/submit_trait", methods=['POST'])
def submit_trait():
    idx = request.form['traits']
    password = request.form['pass']
    if password == "scbd2019jaya":
        db = connect()
        cur = db.cursor()
        cur.execute("SELECT * FROM ontologi_vote WHERE id = '{}'".format(idx))
        res = []
        for row in cur.fetchall():
            res.append(row)
        cur.execute("SELECT COUNT(*) FROM ontologi WHERE words = '{}'".format(res[0][1]))
        words_counts = cur.fetchone()[0]
        cur.close()
        if words_counts == 0:
            cur = db.cursor()
            cur.execute("INSERT INTO ontologi (words, traits, subtraits) VALUES ('{}', '{}', '{}')".format(res[0][1], res[0][2], res[0][2]))
            db.commit()
            cur.close()
            cur = db.cursor()
            cur.execute("DELETE FROM ontologi_vote WHERE texts = '{}'".format(res[0][1]))
            db.commit()
            cur.close()
            db.close()
            flash('Sudah berhasil ditambahkan')
            return redirect('list_new_traits')
        else:
            return redirect('view_submit_traits')
    else:
        redirect('view_submit_traits')

@app.route("/delete_trait", methods=['POST'])
def delete_trait():
    idx = request.form['traits']
    password = request.form['pass']
    if password == "scbd2019jaya":
        db = connect()
        cur = db.cursor()
        cur.execute("DELETE FROM ontologi_vote WHERE id = '{}'".format(idx))
        db.commit()
        cur.close()
        db.close()
        return redirect('list_new_traits')
    else:
        redirect('view_delete_traits')
    
if __name__ == "__main__":
    app.run(debug=True)

# from flask import Flask, request, render_template
# from db_helper import connect
# import pandas as pd
# import re
# import os

# app = Flask(__name__)
# application = app

# IMAGE_FOLDER = os.path.join('static', 'img')
# app.config['IMAGE_FOLDER'] = IMAGE_FOLDER


# @app.route("/")
# def main():
#     return render_template('index.html')
    
# @app.route("/about")
# def about():
#     return render_template('about.html')

# @app.route("/view",methods=['POST'])
# def view():
#     sent = request.form['input_user']
#     sent = sent.lower()
#     sent = re.sub(r'[^a-z]', ' ', sent)
#     tokens = sent.split()

#     list_traits = ['Aggreeableness', 'Conscientiousness', 'Extraversion', 'Neuroticism', 'Openness']
#     list_freq = [0, 0, 0, 0, 0]
#     i = 0
    
#     db = connect()

#     while i < len(tokens):
#         temp = []
#         temp_traits = []
#         cur = db.cursor()
#         cur.execute("SELECT * FROM ontologi WHERE words like '%" + tokens[i] + "%'")
#         for row in cur.fetchall():
#             temp.append(row[1])
#             temp_traits.append(row[2])
#         maks = 0
#         trait = ''
#         cur.close()
#         for k in range(len(temp)):
#             if re.sub('_', ' ', temp[k].lower()) in sent:
#                 if len(temp[k].split('_')) > maks:
#                     trait = temp_traits[k]
#                     maks = len(temp[k].split('_'))
#         if maks > 0:
#             list_freq[list_traits.index(trait)] += 1
#             i += maks
#         else:
#             i += 1
            
#     db.close()

#     return render_template('result.html', trait = list_traits, freq = list_freq, len = len(list_freq))

# if __name__ == "__main__":
#     app.run()



