from flask import Flask, request, render_template 
import json
app = Flask(__name__)

with open('big-hw-01.json', 'r', encoding='utf-8') as f:
    hw01 = json.load(f)
with open('big-hw-02.json', 'r', encoding='utf-8') as f:
    hw02 = json.load(f)

students = []
for idx, item in enumerate(hw01 + hw02, 1):
    if item[""]:  
        student = next((s for s in students if s["ФИО"] == item[""]), None)
        if not student:
            students.append({
                "id": str(idx),
                "ФИО": item[""],
                "Группа": str(item["Группа"]),
                "Баллы": {
                    "hw-01": 0,
                    "hw-02": 0
                }
            })
            student = students[-1]

        if item in hw01:
            student["Баллы"]["hw-01"] = float(item["Баллы"]) if item.get("Баллы") and str(item["Баллы"]).strip() else 0
        elif item in hw02:
            student["Баллы"]["hw-02"] = float(item["Баллы"]) if item.get("Баллы") and str(item["Баллы"]).strip() else 0

@app.route('/names')
def get_names():
    return {'names': [s["ФИО"] for s in students]}

@app.route('/<hw_name>/mean_score')
def get_hw_mean(hw_name):
    if hw_name not in ['hw-01', 'hw-02']:
        return {'error': 'Invalid homework name'}, 400
    
    scores = [s["Баллы"][hw_name] for s in students if hw_name in s["Баллы"]]
    if not scores:
        return {'mean_score': 0}
    return {'mean_score': round(sum(scores)/len(scores), 2)}

@app.route('/<hw_name>/<group_id>/mean_score')
def get_hw_group_mean(hw_name, group_id):
    if hw_name not in ['hw-01', 'hw-02']:
        return {'error': 'Invalid homework name'}, 400
    if group_id not in ['24137', '24144', '24171']:
        return {'error': 'Group not found'}, 404
    
    scores = [s["Баллы"][hw_name] for s in students 
             if s["Группа"] == group_id and hw_name in s["Баллы"]]
    if not scores:
        return {'mean_score': 0}
    return {'mean_score': round(sum(scores)/len(scores), 2)}

@app.route('/mean_score')
def get_mean_score_params():
    hw_name = request.args.get('hw_name')
    group_id = request.args.get('group_id')
    
    if not hw_name:
        return {'error': 'hw_name parameter is required'}, 400
    if hw_name not in ['hw-01', 'hw-02']:
        return {'error': 'Invalid homework name'}, 400
    
    filtered = [s for s in students if not group_id or s["Группа"] == group_id]
    scores = [s["Баллы"][hw_name] for s in filtered if hw_name in s["Баллы"]]
    
    if not scores:
        return {'mean_score': 0}
    return {'mean_score': round(sum(scores)/len(scores), 2)}

@app.route('/mark')
def get_mark():
    student_id = request.args.get('student_id')
    group_id = request.args.get('group_id')
    
    if not (student_id or group_id):
        return {'error': 'Must provide student_id or group_id'}, 400
    if student_id and group_id:
        return {'error': 'Provide either student_id or group_id, not both'}, 400
    
    if student_id:
        student = next((s for s in students if s["id"] == student_id), None)
        if not student:
            return {'error': 'Student not found'}, 404
        
        total = sum(student["Баллы"].values())
        if total >= 50:
            mark = 5
        elif total >= 30:
            mark = 4
        elif total >= 1:
            mark = 3
        else:
            mark = 2
        return {'mark': mark}
    
    if group_id:
        group_students = [s for s in students if s["Группа"] == group_id]
        if not group_students:
            return {'error': 'Group not found'}, 404
            
        marks = []
        for s in group_students:
            total = sum(s["Баллы"].values())
            if total >= 50:
                mark = 5
            elif total >= 30:
                mark = 4
            elif total >= 1:
                mark = 3
            else:
                mark = 2
            marks.append(mark)
            
        if not marks:
            return {'average_mark': 0}
        return {'average_mark': round(sum(marks)/len(marks), 2)}

@app.route('/course_table')
def course_table():
    hw_name = request.args.get('hw_name')
    if not hw_name:
        return {'error': 'Parameter hw_name is required'}, 400
    if hw_name not in ['hw-01', 'hw-02']:
        return {'error': 'Invalid homework name'}, 400
    
    group_id = request.args.get('group_id')
    
    filtered_students = students
    if group_id:
        filtered_students = [s for s in students if s["Группа"] == group_id]
        
    table_data = []
    for student in filtered_students:
        if hw_name in student["Баллы"]:
            score = student["Баллы"].get(hw_name, 0)  # Защита от отсутствующих значений
            table_data.append({
                'name': student["ФИО"],
                'group': student["Группа"],
                'score': score
            })
    
    return render_template('tablisa.html',
                         hw_name=hw_name,
                         group_id=group_id if group_id else 'All Groups',
                         students=table_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, debug=True)