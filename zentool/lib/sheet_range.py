from functools import reduce


class SheetRange:

    """
    A Spreadsheet Range (2 dimensional array of cells).
    Implemented as a sparse matrix using dicts of dicts.
    """

    class Cell:
        """
        Our representation of a cell.
        """
        def __init__(self, value=None, value_type=None, bg=None):
            self.value = value
            self.type = value_type
            self.bg = bg

        TYPE_TO_GOOGLE_CELL_TYPE = {
            'string': 'stringValue',
            'formula': 'formulaValue',
            'number': 'numberValue'
        }

        def __str__(self):
            return f"Cell(\"{self.value}\")"

        def __repr__(self):
            return self.__str__()

        def to_google_cell_data(self):
            cell_data = {}
            cell_data['userEnteredValue'] = {self.TYPE_TO_GOOGLE_CELL_TYPE[self.type]: self.value}
            if self.bg:
                # TODO
                cell_data['userEnteredFormat'] = {
                    "backgroundColor": {
                        "red": "%.2f" % (self.bg['red'] / 255),
                        "green": "%.2f" % (self.bg['green'] / 255),
                        "blue": "%.2f" % (self.bg['blue'] / 255)
                    }
                }
            return cell_data

    def __init__(self):
        self.cols = dict()

    def __setitem__(self, key, value):
        # TODO: allow it to take ('A', 1) or "A1" or (1, 1)
        colnum, rownum = key
        if colnum not in self.cols:
            self.cols[colnum] = dict()
        if type(value) in [int, float]:
            cell_type = 'number'
        elif type(value) == str:
            cell_type = 'formula' if value.startswith('=') else 'string'
        else:
            raise RuntimeError(f"Can't establish cell type for {value}")

        self.cols[colnum][rownum] = self.Cell(value=value, value_type=cell_type)

    def __getitem__(self, item):
        # TODO: allow it to take ('A', 1) or "A1" or (1, 1)
        colnum, rownum = item
        return self.cols.get(colnum, {}).get(rownum, None)

    def __str__(self):
        if self.is_empty:
            return f"Range(EMPTY)"
        else:
            return f"Range({self.name}, {self.cols})"

    def __repr__(self):
        return self.__str__()

    @property
    def is_empty(self):
        return len(self.cols) == 0

    @property
    def name(self):
        """
        :return: a spreadsheet range name that encompasses all the data e.g. "A1:B2"
        """
        return f"{self.lowest_col}{self.lowest_row}:{self.highest_col}{self.highest_row}"

    @property
    def lowest_col(self):
        colnames = sorted(self.cols.keys())
        return colnames[0]

    @property
    def highest_col(self):
        colnames = sorted(self.cols.keys())
        return colnames[-1]

    @property
    def lowest_row(self):
        lists_of_rownums = [list(col.keys()) for colname, col in self.cols.items()]
        list_of_rownums = reduce(lambda l1, l2: l1+l2, lists_of_rownums)
        return sorted(list_of_rownums)[0]

    @property
    def highest_row(self):
        lists_of_rownums = [list(col.keys()) for colname, col in self.cols.items()]
        list_of_rownums = reduce(lambda l1, l2: l1+l2, lists_of_rownums)
        return sorted(list_of_rownums)[-1]

    def to_array(self):
        """
        :return: an array of arrays containing the data (rows, cols)
        """
        rows = []
        for rownum in range(self.lowest_row, self.highest_row+1):
            row = []
            for colnum in range(ord(self.lowest_col), ord(self.highest_col)+1):
                colname = chr(colnum)
                row.append(self[colname, rownum])
            rows.append(row)
        return rows

    def to_google_grid_range(self, sheet_id=0):
        return {
            'sheetId': sheet_id,
            'startRowIndex': self.lowest_row - 1,
            'endRowIndex': self.highest_row,
            'startColumnIndex': self._column_letter_to_0_based_integer(self.lowest_col),
            'endColumnIndex': self._column_letter_to_0_based_integer(self.highest_col) + 1
        }

    def to_google_rows(self):
        rows = []
        for rownum in range(self.lowest_row, self.highest_row+1):
            row = {'values': []}
            for colnum in range(ord(self.lowest_col), ord(self.highest_col)+1):
                col_letter = chr(colnum)
                cell = self[col_letter, rownum]
                cell_data = cell.to_google_cell_data() if cell else {}
                row['values'].append(cell_data)
            rows.append(row)
        return rows

    def _column_letter_to_0_based_integer(self, col_letter):
        return ord(col_letter) - 65
