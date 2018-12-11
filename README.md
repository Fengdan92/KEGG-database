# Overview
This is repository consists of two parts:
* Codes to reconstruct genome-scale metabolic networks automatically from KEGG database ("multi" and "database" folder)
* Codes to conduct Flux Balance Analysis (FBA) on an established E.coli model i*ML*1515, and calculate the Louvain modularity for the resulting bipartite directed weighted network ("fba and modularity" folder).

# Instructions
## Reconstruction of genome-scale metabolic networks automatically from KEGG database ("multi" and "database" folder)
* Run multi/multi_preparation.py
  * update local KEGG database (optional) - files are saved to /database
  * convert the database .xlsx files to python dictionaries. Establish bacteria - enzyme relations, and enzyme - reactant pairs relations.
  * save the python dictionaries as pickle files.
* Run multi/multi.py
  * read .pkl files
  * for each bacterium, print its full lists of reactant pairs.
  * for each bacterium, calculate modularity of its metabolite network using directed Louvain algorithm.
  * graph the metabolite network and remove isolates.
  * calculate modularity again after isolates are removed.
  * graph the new metabolite network
 
 ## Flux balance analysis and modularity calculation based on E. coli model iML1515 ("fba and modularity" folder)
* FBA in matlab:
initCobraToolbox  
model=readCbModel('iML1515.mat');  
modelGluAerobic = model;  
modelGluAerobic = changeObjective (modelGluAerobic, 'BIOMASS_Ec_iML1515_core_75p37M');  
FBAGluAerobic = optimizeCbModel(modelGluAerobic,'max');  
(Change maximum uptake rate as needed. In my case, I was changing maximum glucose uptake rate and maximum oxygen uptake rate) 
T = table(modelGluAerobic.rxns, modelGluAerobic.rxnNames, FBAGluAerobic.v);
writetable(T,'Flux_GluAerobic.xlsx','FileType','spreadsheet');
* Local preparation ("localPrep" folder). Assume the parameter for FBA set is named "g0"
  * run Parse_vertex_pairs.ipynb or Parse_vertex_pairs.py to obtain dict_all.pkl and dict_subsys.pkl
  * run Save_flux.ipynb or Save_flux.py to obtain dict_flux_g0.pkl
  * run Save_input.ipynb to obtain lst_reactions_g0.pkl, lst_metabolites_g0.pkl, and edges_g0.pkl
* Run modularity calculation on a computer cluster
  * upload everything to a computer cluster
  * submit job through submit_job.slurm
   * g0.py will be run multiple times. g0.py calls the bidiLouvain.py script to calculate modularity.

fba and modularity/bidiLouvain/ contains the codes for calculating modularity for a bipartite directed weighted network.

-------------------
Updated 12-11-2018
