import decimal
import numpy as np

def cell_dims(x1, y1, x2, y2):
    return x1, y1, x2 - x1, y2 - y1


def cell_dims_from_list(list_onbj):
    return cell_dims(list_onbj[0], list_onbj[1], list_onbj[2], list_onbj[3])


def drange(x, y, jump):
    while x < y:
        yield float(x)
        x += decimal.Decimal(jump)


def get_row_points(box, num_of_scanned_rows):
    space = (box[3] - box[1]) / num_of_scanned_rows
    row_points = list(drange(box[1], box[3], f'{space}'))
    final_row_points = list(np.rint(np.asarray(row_points)).astype(int))
    return final_row_points


def get_col_points(box, col_coefs):
    col_delta = box[2] - box[0]
    cols_points = []
    for col_coef in col_coefs:
        cols_points.append(col_delta * col_coef)

    temp_list = []
    for i in range(len(cols_points)):
        this_int = box[0]
        for j in range(i + 1):
            this_int += cols_points[j]
        temp_list.append(this_int)

    final_col_points = np.array(temp_list)
    final_col_points = list(np.rint(final_col_points).astype(int))
    final_col_points = [box[0]] + final_col_points + [box[2]]
    return final_col_points


def get_cells(x_range, y_range):
    cells = {}
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            try:
                cells[i, j] = tuple([x, y, x + x_range[i + 1], y + y_range[j + 1]])
            except:  # lazy
                pass
    return cells