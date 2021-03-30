import psycopg2 #postgresql
import re
import sys
import pytest

class QueryCheck:
    def dbconnect(self, db, username, password):
        self.con = psycopg2.connect(database=db, user=username, password=password, host="webcourse.cs.nuim.ie",
                               port="5432")
        print("Database opened successfully")

    def check(self, file1, file2):
        file_rows = open(file1, "r")
        file_teacher = open(file2, "r")

        no_of_rows = []
        for line in file_rows: #read the number of rows of each query and append it to the array
            match = re.search(r'\d+', line)
            if match:
                no_of_rows.append(int(line[match.start():match.end()]))

        teacher = [] #read the teachers query in the file and append it to the array
        for line in file_teacher:
            teacher.append(line)

        cursor = self.con.cursor()
        count = 0
        for query in teacher:
            print("showing result for query number:"+str(count+1))
            cursor.execute(query) #execute student's query
            if 'SELECT' in query.upper():
                rows_student = cursor.fetchall()
                print(len(rows_student))
            else:
                rows_student = cursor.rowcount
                print(rows_student)
            print(no_of_rows[count])
            count+=1

        

    def evaluate(self, file1, file2, file3):
        file_rows = open(file1, "r")
        file_teacher = open(file2, "r")
        file_student = open(file3, "r")

        no_of_rows = []
        for line in file_rows:
            match = re.search(r'\d+', line)
            if match:
                no_of_rows.append(int(line[match.start():match.end()]))

        teacher = []
        for line in file_teacher:
            teacher.append(line)

        teacher_query = []
        teacher_response = []
        substring_list = ["select","where","insert","alter","update","delete"]
        for line in teacher:
            if any(substring in line.lower() for substring in substring_list):
                teacher_query.append(line)
            else:
                teacher_response.append(line)

        student = []
        for line in file_student:
            student.append(line)

        student_query = []
        student_response = []
        for line in student:
            if any(substring in line.lower() for substring in substring_list):
                student_query.append(line)
            else:
                student_response.append(line)

        marks1 = self.evaluateTextAnswers(student_response, teacher_response)
        marks2 = self.evaluateSQLQueries(no_of_rows, student_query, teacher_query)

        return ((marks1+marks2)/len(teacher))*100
        

    def evaluateTextAnswers(self, arr_student, arr_teacher):
        marks = 0

        for i in range(0,len(arr_student)):
            print('Teacher: {} === Student: {}'.format(arr_teacher[i], arr_student[i]))
            student = ''.join(e for e in arr_student[i] if e.isalnum())
            teacher = ''.join(e for e in arr_teacher[i] if e.isalnum())
            if (student.lower() == teacher.lower()):
                marks = marks+1

        return marks

    def evaluateSQLQueries(self, no_of_rows, arr_student, arr_teacher):
        cursor = self.con.cursor()
        count = 0
        marks = 0

        for query in arr_student:
            print("showing result for query number:"+str(count))
            try: 
                cursor.execute(query) #execute student's query
            except Exception as er:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                line_number = exception_traceback.tb_lineno
                print('{}: {}'.format(exception_type, line_number))
                self.con.rollback()
                count+=1
                continue
            if 'SELECT' in query.upper():
                rows_student = cursor.fetchall()
                print('{} == {}'.format(len(rows_student), no_of_rows[count]))
                if len(rows_student) == no_of_rows[count]:
                    cursor.execute(arr_teacher[count])
                    rows_teacher = cursor.fetchall() #execute teacher's query
                    print(set(rows_student) == set(rows_teacher))
                    if set(rows_student) == set(rows_teacher): #if the results are duplicate
                        print("The queries produce duplicate results")
                        marks = marks + 1
                    else: #otherwise
                        flag = 0
                        for i in range(0, len(rows_teacher)): #while ensuring number of rows remain ssame
                            if set(rows_teacher[i]).issubset(set(rows_student[i])) or set(rows_student[i]).issubset(set(rows_teacher[i])):
                                flag += 1
                        if flag == len(rows_teacher):
                            print("The queries are a subset of each other!")
                else:
                    print('Incorrect answer!!!')
            else:
                rows_student = cursor.rowcount
                print('{} == {}'.format(rows_student, no_of_rows[count]))
                if rows_student == no_of_rows[count]:                    
                    marks = marks + 1
                else:
                    print('Incorrect answer')
              
            count+=1

        cursor.close()
        return marks

queryChecker = QueryCheck()
queryChecker.dbconnect("cs621","p200077","23WIBInQvP")
f1 = "exp_rows.txt" # path to rows file
f2 = "exp_teacher.txt" # path to teacher query
f3 = "exp_studentC.txt" # path to students query
#queryChecker.check(f1, f2)
print("You scored {:.2f}".format(queryChecker.evaluate(f1, f2, f3)))
#queryChecker.evaluate(f1, f2, f3)


def test_case1():
    f1 = "rows1.txt"
    f2 = "teacher1.txt"
    f3 = "student1.txt"
    assert queryChecker.evaluate(f1, f2, f3) == 70

def test_case2():
    f1 = "rows2.txt"
    f2 = "teacher2.txt"
    f3 = "student2.txt"
    assert queryChecker.evaluate(f1, f2, f3) == 90

def test_case3():
    f2 = "teacher3.txt"
    f3 = "student3.txt"
    assert queryChecker.evaluate(f1, f2, f3) == 100