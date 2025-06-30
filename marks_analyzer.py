from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os


app = Flask(__name__)
students = []

@app.route('/')
def index():
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    try:
        marks = int(request.form['marks'])
    except ValueError:
        return render_template('index.html', message="Invalid marks input!", students=students)

    students.append({'name': name, 'marks': marks})
    return render_template('index.html', message=f"{name} added successfully", students=students)

@app.route('/delete/<int:index>')
def delete_student(index):
    if 0 <= index < len(students):
        removed = students.pop(index)
        message = f"Removed {removed['name']} successfully."
    else:
        message = "Invalid student index."
    return render_template('index.html', message=message, students=students)
@app.route('/clear')
def clear_students():
    students.clear()
    return render_template('index.html', message="All student data cleared!", students=students)
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.csv')):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            for _, row in df.iterrows():
                name = str(row['Name'])
                marks = int(row['Marks'])
                students.append({'name': name, 'marks': marks})

            return render_template('index.html', message="Excel data imported!", students=students)
        except Exception as e:
            return render_template('index.html', message=f"Error reading file: {e}", students=students)
    return render_template('index.html', message="Invalid file type", students=students)

@app.route('/analyze')
def analyze():
    if not students:
        return "No students added"

    total = 0
    passed = 0
    grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
    highest = students[0]
    lowest = students[0]

    for s in students:
        marks = s['marks']
        total += marks

        if marks > highest['marks']:
            highest = s
        if marks < lowest['marks']:
            lowest = s
        if marks >= 40:
            passed += 1

        if marks >= 85:
            grades['A'] += 1
        elif marks >= 70:
            grades['B'] += 1
        elif marks >= 55:
            grades['C'] += 1
        elif marks >= 40:
            grades['D'] += 1
        elif marks >= 30:
            grades['E'] += 1
        else:
            grades['F'] += 1

    avg = total / len(students)
    failed = len(students) - passed

    # Generate bar chart and save in /static/
    import matplotlib.pyplot as plt
    import os
    os.makedirs('static', exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.bar(grades.keys(), grades.values(), color='red')
    plt.title('Grade Distribution')
    plt.xlabel('Grades')
    plt.ylabel('Number of Students')
    plt.savefig('static/grades_chart.png')
    plt.close()

    return render_template('result.html',
                           avg=avg,
                           highest=highest,
                           lowest=lowest,
                           passed=passed,
                           failed=failed,
                           grades=grades)


if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
