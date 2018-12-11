'''

request_api_functions
~~~~~~~~~~~~~

Contains functions that save information to .xlsx files.

python 2.7.5
Nov 10, 2017

'''
from xlsxwriter import Workbook

def savexls_org(dir, filename, lst_org):
	'''
	Save organism info into a .xlsx file.

	Parameters
	----------
	dir : string 
		Directory to save the file
		End this string with '/'
	filename : string
		Desired name for the file
	lst_org : list of dictionaries
		List of organism information. Each dictinary
		contains keys: 'Code','Abbr','Name','Type'

	Returns
	-------
	None
	'''
	print('>>> Saving organism info... File name: '+ filename)

	header_lst = ['Code','Abbr','Name','Type']
	wb_org = Workbook(dir + filename)
	ws_org = wb_org.add_worksheet("Sheet 1")

	header_row = 0 
	for col in range(0,len(header_lst)):
		ws_org.write(header_row, col, header_lst[col])

	row = 1
	for org in lst_org:
		for _key, _value in org.items():
			col = header_lst.index(_key)
			ws_org.write(row, col, _value)
		row = row + 1
	
	wb_org.close()

	return None




def savexls_bact(dir, filename, lst_bact):
	'''
	Save bacteria info into a .xlsx file.

	Parameters
	----------
	dir : string 
		Directory to save the file
		End this string with '/'
	filename : string
		Desired name for the file
	lst_bact : list of dictionaries
		List of bacteria information. Each dictinary
		contains keys: 'Code','Abbr','Name','Type'

	Returns
	-------
	None
	'''
	print('>>> Saving bacteria info... File name: '+ filename)


	header_lst = ['Code','Abbr','Name','Type']
	wb_bact = Workbook(dir + filename)
	ws_bact = wb_bact.add_worksheet("Sheet 1")

	header_row = 0 
	for col in range(0,len(header_lst)):
		ws_bact.write(header_row, col, header_lst[col])

	row = 1 
	for bact in lst_bact:
		for _key, _value in bact.items():
			col = header_lst.index(_key)
			ws_bact.write(row, col, _value)
		row = row + 1

	wb_bact.close()

	return None 



def savexls_ec_bact(dir, filename, lst_ec_bact, lst_abbr):
	'''
	Save enzyme - bacteria relations into a .xlsx file.

	Parameters
	----------
	dir : string 
		Directory to save the file
		End this string with '/'
	filename : string
		Desired name for the file
	lst_ec_bact : list of dictionaries
		List of EC - bacteria relations. Each dictinary
		contains keys: 'EC' and bacteria names. 
		'1' means the enzyme is encoded by this bacteria.
		'0' means the enzyme is not encoded by this bacteria.
	lst_abbr : list of strings
		Serve as headers

	Returns
	-------
	None
	'''
	print('>>> Saving EC - bacteria relations... File name: '+ filename)
	
	header_lst = ['EC'] + lst_abbr
	wb_ec_bact = Workbook(dir + filename)
	ws_ec_bact = wb_ec_bact.add_worksheet("Sheet 1")

	header_row = 0 
	for col in range(0,len(header_lst)):
		ws_ec_bact.write(header_row, col, header_lst[col])

	row = 1 
	for unit in lst_ec_bact:
		for _key, _value in unit.items():
			col = header_lst.index(_key)
			ws_ec_bact.write(row, col, _value)
		row = row + 1

	wb_ec_bact.close()

	return None



def savexls_ec_reac(dir, filename, lst_ec_reac):
	'''
	Save enzyme - reaction relations into a .xlsx file.

	Parameters
	----------
	dir : string 
		Directory to save the file
		End this string with '/'
	filename : string
		Desired name for the file
	lst_ec_reac: list of dictionaries
		List of EC - reaction relations. Each dictinary
		contains keys: 'EC' and 'Reactions'. 
		'Reactions' corresponds to a list of strings,
		which are the names of the reactions.

	Returns
	-------
	None
	'''
	print('>>> Saving EC - reaction relations... File name: '+ filename)

	wb_ec_reac = Workbook(dir + filename)
	ws_ec_reac = wb_ec_reac.add_worksheet("Sheet 1")

	ws_ec_reac.write(0, 0, 'EC')
	ws_ec_reac.write(0, 1, 'Reactions')

	row = 1
	for unit in lst_ec_reac:
		ws_ec_reac.write(row, 0, unit['EC'])
		col = 1;
		for reac in unit['Reactions']:
			ws_ec_reac.write(row, col, reac)
			col = col + 1
		row = row + 1

	wb_ec_reac.close()

	return None