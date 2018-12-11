import multi_utils as mu
import pickle

update_database = raw_input('>>> Do you want to update the local KEGG database? (y or n):\n')
if update_database == 'y':
	mu.request_api()

filename_ec_bact = raw_input('>>> Name of the ec_bact file:\n')
filename_ec_reac = raw_input('>>> Name of the ec_reac file:\n')
filename_db = raw_input('>>> Name of the bioreaction database:\n')
[lst_bact, dict_bact_ec, dict_ec_pairs] = mu.obtain_dict(filename_ec_bact=filename_ec_bact, filename_ec_reac=filename_ec_reac, filename_db=filename_db)

afile = open(r'lst_bact.pkl', 'wb')
pickle.dump(lst_bact, afile)
afile.close()

bfile = open(r'dict_bact_ec.pkl', 'wb')
pickle.dump(dict_bact_ec, bfile)
bfile.close()

cfile = open(r'dict_ec_pairs.pkl', 'wb')
pickle.dump(dict_ec_pairs, cfile)
cfile.close()