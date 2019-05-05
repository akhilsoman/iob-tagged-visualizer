import os
import csv
import tempfile 
import webbrowser
from yattag import Doc
from collections import Counter

colors = ["#66815B", "#A4D389", "#69BD45", "#39bb01", "#7AECED"]
css = 'span {font-size: 20px;line-height: 50px;display: inline-block;} span.token {color: #fff;padding: 5px;line-height: 20px;} li {list-style: none;margin: 5px;float: left;}'

def getElement(token):
    if token["weight"] > 4 :
        return '<span style=background:'+ colors[4]+' class="token" >' + token["token"] + '</span>'
    elif token["weight"] > 0:
        return '<span style=background:'+ colors[token["weight"]-1] +' class="token" >' + token["token"]+ '</span>'
    else:
        return '<span>' + token["token"]+ '</span>'

def generateHTMLOutput(content, skills, file):
    skill_list = ""
    skills.sort(key=lambda x: x['weight'], reverse=True)

    for skill in skills: 
        skill_list += '<li>' + getElement(token=skill) + '</li>'

    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            with doc.tag('style', type='text/css'):
                doc.asis(css)
        with tag('body'):
            with tag('h1'):
                text(file)
            with tag('p', id = 'main'):
                doc.asis(content)
            with tag('div', id='skills'):
                with tag('ul'):
                    doc.asis(skill_list)

    result = doc.getvalue()
    
    tmp=tempfile.NamedTemporaryFile(delete=False)
    path=tmp.name+'.html'

    f=open(path, 'w')
    f.write(result)
    f.close()

    webbrowser.open('file://' + path)

def processFile(tsvin):
    weightage = []
    sequence = [None] * 6
    sequences = []
    skills=[]
    content=""
    tokens=[]
    for idx, row in enumerate(tsvin):
        if idx == 0:
            continue

        # generating weightage metrix
        weightage.append({
            "token": row[1],
            "weight":row[2:].count('B') + row[2:].count('I')
        })
        
        # generating seqeuences 
        for i, tag in enumerate(row[2:]):
            if tag == 'B':
                if sequence[i] is not None:
                    sequences.append(sequence[i].strip(" ,"))
                sequence[i] = None
                sequence[i] = str(row[1]) + " "
            elif tag == 'I' and sequence[i] is not None :
                sequence[i] += str(row[1]) + " "
            elif sequence[i] is not None:
                sequences.append(sequence[i].strip(" ,"))
                sequence[i] = None

    for j, seq in enumerate(Counter(sequences).keys()):
            skills.append({
                "token": seq + " (" + str(Counter(sequences).values()[j])+ ")",
                "weight": Counter(sequences).values()[j]
            })

    for token in weightage:
        content += getElement(token=token) + " "

    return content, skills

if __name__ == '__main__':
    alldicts = []
    path = 'resources/'
    for file in os.listdir(path):
        full_filename = "%s/%s" % (path, file)
        if os.path.splitext(file)[1] == ".tsv":
            alldicts.append(full_filename)
    for jfile in alldicts:
        with open(jfile, 'rb') as tsvin:
            status = {"file": os.path.basename(jfile), "parsed" : False}
            tsvin = csv.reader(tsvin, delimiter='\t')
            try:
                content, skills = processFile(tsvin=tsvin)
                generateHTMLOutput(content=content, skills=skills, file=os.path.basename(jfile))
                status["parsed"] = True
            except Exception as e:
                raise Exception(e)
            finally:
                print(status)
            

                    
