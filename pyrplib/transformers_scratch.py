#sys.path.insert(0,"%s/rankability_toolbox_dev"%home)
#sys.path.insert(0,"%s/RPLib"%home)

# -

# ### Baseline 0001

# **Function to compute a D matrix from games using hyperparameters**

"""
def compute_D(game_df,team_range,direct_thres,spread_thres):
    map_func = lambda linked: pyrankability.construct.support_map_vectorized_direct_indirect(linked,direct_thres=direct_thres,spread_thres=spread_thres)
    Ds = pyrankability.construct.V_count_vectorized(game_df,map_func)
    for i in range(len(Ds)):
        Ds[i] = Ds[i].reindex(index=team_range,columns=team_range)
    return Ds
"""