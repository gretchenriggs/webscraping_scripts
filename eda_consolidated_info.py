import pandas as pd


if __name__ == '__main__':
    df = pd.read_csv("res_2016_proptax_permitinfo_consolidated.csv")
    df2 = pd.read_csv("com_2016_proptax_permitinfo_consolidated.csv")
    df_all = pd.concat([df, df2])
    df_all.reset_index(drop=False, inplace=True)
