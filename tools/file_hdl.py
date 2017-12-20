import csv


def load_csv(path, col_type=None):
    if col_type is None:
        col_type = {}
    final_list = []
    try:
        with open(path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # noinspection PyTypeChecker
                if len(col_type.keys()) > 0:
                    try:
                        for key in col_type.keys():
                            if col_type[key] == 'float':
                                row[key] = float(row[key])
                            elif col_type[key] == 'int':
                                row[key] = int(float(row[key]))
                        final_list.append(row)
                    except ValueError as e:
                        # FIXME should be logging
                        print('Loading csv error: %s %s' % (e, '%s %r' % (path, row)))
                else:
                    final_list.append(row)
            for row in reader:
                final_list.append(row)
        return final_list
    except FileNotFoundError:
        return None
