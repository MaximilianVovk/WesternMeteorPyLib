# file used to generate different datasets and train models on those datasets, all in sequence

cd /home/jkambul2/WesternMeteorPyLib
#python -m wmpl.MetSim.ML.GenerateSimulations /home/jkambul2/files/fixed_erosion_dataset 6000000 --noerosion --fixed 0 0 0 0 0 1 1 1 1 1
#python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/fixed_erosion_dataset /home/jkambul2/files/trained_models -mn fixederosion --grouping 256 50

# python -m wmpl.MetSim.ML.GenerateSimulations /home/jkambul2/files/unfixed_sigma 600000 --fixed 0 0 0 1 0 1 1 1 1 1 --noerosion
# python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/unfixed_sigma /home/jkambul2/files/trained_models -mn unfixed_sigma --grouping 256 50

# python -m wmpl.MetSim.ML.GenerateSimulations /home/jkambul2/files/unfixed_erh_rho 600000 --fixed 0 0 0 0 1 0 1 1 1 1
# python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/unfixed_erh_rho /home/jkambul2/files/trained_models -mn unfixed_erh_rho --grouping 256 50

# python -m wmpl.MetSim.ML.GenerateSimulations /home/jkambul2/files/unfixed_erh_sigma 600000 --fixed 0 0 0 1 0 0 1 1 1 1
# python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/unfixed_erh_sigma /home/jkambul2/files/trained_models -mn unfixed_erh_sigma --grouping 256 50

# python -m wmpl.MetSim.ML.GenerateSimulations /home/jkambul2/files/log_sigma_rho 600000 --fixed 0 0 0 0 0 1 1 1 1 1 --noerosion
# python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/log_sigma_rho /home/jkambul2/files/trained_models -mn log_sigma_rho --grouping 256 50

# python -m wmpl.MetSim.ML.GenerateSimulations /home/jkambul2/files/fixederosion_restrictedrange_dataset 600000 --noerosion --fixed 0 0 0 0 0 1 1 1 1 1
# python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/fixederosion_restrictedrange_dataset /home/jkambul2/files/trained_models -mn fixederosion_reduceddomain --grouping 256 50 --roi -1
python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/fixederosion_restrictedrange_dataset /home/jkambul2/files/trained_models -mn lowerleft_fixederosion --grouping 256 50 --roi 0
python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/fixederosion_restrictedrange_dataset /home/jkambul2/files/trained_models -mn lowerright_fixederosion --grouping 256 50 --roi 1
python -m wmpl.MetSim.ML.FitErosion /home/jkambul2/files/fixederosion_restrictedrange_dataset /home/jkambul2/files/trained_models -mn bottom_fixederosion --grouping 256 50 --roi 2
