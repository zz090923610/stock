def csv_from_excel():
    
in_xls='/home/zhangzhao/Downloads/test.xls'
out_csv='/home/zhangzhao/test_output.csv'


wb = xlrd.open_workbook(in_xls)
sh = wb.sheet_by_name(sheet)
sheet=wb.sheet_names()[0]
dict_list =[]
title_list = sh.row_values(1)
if sh.nrows > 2:
	for rownum in range(2, sh.nrows):
		tmp_dict= {}
		for (col_name,col_val) in zip(title_list,sh.row_values(rownum)):
			tmp_dict[col_name] = col_val
		dict_list.append(tmp_dict)