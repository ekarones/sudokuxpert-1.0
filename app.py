from flask import Flask, render_template, request, flash, redirect, url_for
import numpy as np
import json
from ortools.sat.python import cp_model

app = Flask(__name__)
app.secret_key = 'my_super_secret_key'
app.config['PROJECT_HOST'] = "https://sudokuxpert-10-production.up.railway.app/"

@app.route('/', methods=['GET', 'POST'])
def home():
    if (request.method == 'POST'):
        sudoku_data = request.form.getlist('cell')
        matrix = convert_to_matrix(sudoku_data)
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] == '':
                    matrix[i][j] = '0'
        matrix_np = np.array(matrix)
        matrix_np = matrix_np.astype(int)
        sudoku = matrix_np
        model = cp_model.CpModel()
        board = {}

        for i in range(9):
            for j in range(9):
                if sudoku[i][j] == 0:
                    board[(i, j)] = model.NewIntVar(1, 9, f'cell_{i}_{j}')
                else:
                    board[(i, j)] = sudoku[i][j]

        for i in range(9):
            model.AddAllDifferent([board[(i, j)] for j in range(9)])
            model.AddAllDifferent([board[(j, i)] for j in range(9)])

        for k in range(3):
            for l in range(3):
                subgrid_vars = []
                for i in range(3):
                    for j in range(3):
                        subgrid_vars.append(board[(3*k+i, 3*l+j)])
                model.AddAllDifferent(subgrid_vars)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            sudoku_solved = np.zeros((9, 9))
            for i in range(9):
                for j in range(9):
                    sudoku_solved[i][j] = solver.Value(board[(i, j)])
            matrix_list = matrix_to_list(sudoku_solved)
            matrix_json = json.dumps(matrix_list)

            matrix_list_o = matrix_to_list(matrix_np)
            matrix_json_o = json.dumps(matrix_list_o)

            return redirect(url_for('show_result', matrix=matrix_json, matrix_o=matrix_json_o))
        else:
            return redirect(url_for('no_result'))

    return render_template('layout.html')


def convert_to_matrix(data):
    matrix = []
    for i in range(0, len(data), 9):
        row = data[i:i + 9]
        matrix.append(row)
    return matrix


def matrix_to_list(matrix):
    return matrix.astype(int).tolist()


@app.route('/result', methods=['GET'])
def show_result():
    matrix = request.args.get('matrix')
    matrix_list = json.loads(matrix)

    matrix_o = request.args.get('matrix_o')
    matrix_list_o = json.loads(matrix_o)

    return render_template('result.html', matrix=matrix_list, matrix_o=matrix_list_o)


@app.route('/error', methods=['GET'])
def no_result():
    return render_template('no_result.html')


if __name__ == '__main__':
    pass
