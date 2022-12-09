#! /usr/bin/env python3

import numpy as np
import pandas as pd
from typing import Optional
from collections import Counter
import sys
import getopt


def is_debug() -> bool:
    gettrace = getattr(sys, 'gettrace', None)

    if gettrace is None:
        return False
    else:
        v = gettrace()
        if v is None:
            return False
        else:
            return True


def find_nearest(array: list | np.ndarray,
                 key: int | float,
                 mode: str,
                 maxi: Optional[int] = 10000,
                 mini: Optional[int] = 0,) -> int | float:
    array = np.asarray(array)
    if mode == 'upper':
        # the smallest element of array GREATER than key
        if key >= np.max(array):
            return maxi
        else:
            return array[array > key].min()
    elif mode == 'lower':
        # the largest element of array LESS than key
        if key <= np.min(array):
            return mini
        else:
            return array[array < key].max()
    else:
        return array[(np.abs(array - key)).argmin()]


def contacts_focus_around_centromeres(formated_contacts_path: str, windows: int, centro_infos_path: str):
    df_centros = pd.read_csv(centro_infos_path, sep='\t', index_col=None)
    df_contacts = pd.read_csv(formated_contacts_path, sep=',', index_col=0)
    df_res = pd.DataFrame()

    for index, row in df_centros.iterrows():
        current_chr = row[0]
        current_centro_pos = row[2]

        left_cutoff = current_centro_pos - windows
        if left_cutoff < 0:
            left_cutoff = 0
        right_cutoff = current_centro_pos + windows
        tmp_df = df_contacts.loc[(df_contacts['chr'] == current_chr) &
                                 (df_contacts['chr_bins'] > left_cutoff) &
                                 (df_contacts['chr_bins'] < right_cutoff)]

        tmp_df.index = range(len(tmp_df))
        current_centro_bin = find_nearest(tmp_df['chr_bins'].values, current_centro_pos, mode='lower')

        for index2, _ in tmp_df.iterrows():
            tmp_df.iloc[index2, 1] -= current_centro_bin

        df_res = pd.concat([df_res, tmp_df])
    df_res.index = range(len(df_res))
    return df_res


def compute_mean_per_fragment(df_centro_bins: pd.DataFrame):
    df_mean = pd.DataFrame()
    df_std = pd.DataFrame()
    bins_counter = dict(Counter(df_centro_bins['chr_bins'].values))
    for b in bins_counter:
        contacts_in_bin = df_centro_bins[df_centro_bins['chr_bins'] == b]
        tmp_df = contacts_in_bin.iloc[:, 3:]
        tmp_mean_df = pd.DataFrame(tmp_df.mean()).T
        tmp_std_df = pd.DataFrame(tmp_df.std()).T
        tmp_mean_df.index = [b]
        tmp_std_df.index = [b]
        df_mean = pd.concat([df_mean, tmp_mean_df])
        df_std = pd.concat([df_std, tmp_std_df])
    return df_mean, df_std


def debug(formated_contacts_path: str, windows: int, centro_infos_path: str):
    df_contacts_centro = contacts_focus_around_centromeres(formated_contacts_path=formated_contacts_path,
                                                        windows=windows,
                                                        centro_infos_path=centro_infos_path)

    df_mean, df_std = compute_mean_per_fragment(df_centro_bins=df_contacts_centro)
    pass


def main(argv=None):
    pass


if __name__ == "__main__":
    if is_debug():
        centro_info = "../../../bash_scripts/aggregate_centro/inputs/S288c_chr_centro_coordinates.tsv"
        formated_contacts = "../../../bash_scripts/aggregate_centro/inputs/formated_contacts_matrix_5kb.csv"
        output = "../../../bash_scripts/aggregate_centro/outputs/"
        windows_range = 150000
        debug(formated_contacts_path=formated_contacts, windows=windows_range, centro_infos_path=centro_info)
    else:
        main()
    print('--- DONE ---')