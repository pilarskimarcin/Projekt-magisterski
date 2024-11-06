# -*- coding: utf-8 -*-
import os
from typing import List, Tuple


def main():
    results_dir: str = "../Wyniki"
    for directory in ListDirectoriesAndFilesInDirectory(results_dir)[0]:
        dir_path: str = f"{results_dir}/{directory}"
        print("=========================================")
        print(directory)
        ParseResultsInDirectory(dir_path)


def ListDirectoriesAndFilesInDirectory(directory_path: str) -> Tuple[List[str], List[str]]:
    _, directories, files = next(os.walk(directory_path))
    return directories, files


def ParseResultsInDirectory(dir_path: str):
    avg_n_dead, avg_avg_RPM, avg_sim_time, avg_avg_help_time, avg_obj_func = CalculateAveragesFromFile(dir_path)
    print(f"Średnia liczba zmarłych: {avg_n_dead}")
    print(f"Średnia ocena RPM poszkodowanych: {avg_avg_RPM}")
    print(f"Średni czas symulacji: {avg_sim_time}")
    print(f"Średni czas pomocy: {avg_avg_help_time}")
    print(f"Średnia wartość funkcji celu: {avg_obj_func}")
    print("Wartość funkcji celu dla średnich wartości: "
          f"{-avg_n_dead + 4 * avg_avg_RPM - 0.25 * avg_sim_time - 0.3 * avg_avg_help_time}")


def CalculateAveragesFromFile(dir_path: str) -> Tuple[float, float, float, float, float]:
    n_dead_list, avg_RPM_list, sim_time_list, avg_help_time_list, obj_func_list = GetDataFromFilesInDirectory(dir_path)
    n: int = len(obj_func_list)
    avg_n_dead: float = sum(n_dead_list) / n
    avg_avg_RPM: float = sum(avg_RPM_list) / n
    avg_sim_time: float = sum(sim_time_list) / n
    avg_avg_help_time: float = sum(avg_help_time_list) / n
    avg_obj_func: float = sum(obj_func_list) / n
    return avg_n_dead, avg_avg_RPM, avg_sim_time, avg_avg_help_time, avg_obj_func


def GetDataFromFilesInDirectory(dir_path) -> Tuple[List[int], List[float], List[int], List[float], List[float]]:
    n_dead_list: List[int] = []
    avg_RPM_list: List[float] = []
    sim_time_list: List[int] = []
    avg_help_time_list: List[float] = []
    obj_func_list: List[float] = []
    for file in ListDirectoriesAndFilesInDirectory(dir_path)[1]:
        file_path: str = f"{dir_path}/{file}"
        with open(file_path, "r", encoding="utf-8") as f:
            n_dead_line, avg_RPM_line, sim_time_line, avg_help_time_line, obj_func_line = f.readlines()[:5]
        if obj_func_line.endswith("Rozwiązanie"):
            print(file)
            raise ValueError
        n_dead_list.append(int(ExtractDataFromLine(n_dead_line)))
        avg_RPM_list.append(float(ExtractDataFromLine(avg_RPM_line)))
        sim_time_list.append(int(ExtractDataFromLine(sim_time_line)))
        avg_help_time_list.append(float(ExtractDataFromLine(avg_help_time_line)))
        obj_func_list.append(float(ExtractDataFromLine(obj_func_line)))
    return n_dead_list, avg_RPM_list, sim_time_list, avg_help_time_list, obj_func_list


def ExtractDataFromLine(line: str) -> str:
    return line.split(":")[1].split(",")[0]


if __name__ == '__main__':
    main()

# =========================================
# S3
# Średnia liczba zmarłych: 12.18
# Średnia ocena RPM poszkodowanych: 7.683600000000007
# Średni czas symulacji: 85.09
# Średni czas pomocy: 48.71060000000001
# Średnia wartość funkcji celu: -17.3311
# Wartość funkcji celu dla średnich wartości: -17.33127999999997
# =========================================
# S7
# Średnia liczba zmarłych: 16.78
# Średnia ocena RPM poszkodowanych: 5.965599999999998
# Średni czas symulacji: 272.14
# Średni czas pomocy: 131.9699
# Średnia wartość funkcji celu: -100.54359999999996
# Wartość funkcji celu dla średnich wartości: -100.54357
# =========================================
# S8
# Średnia liczba zmarłych: 57.36
# Średnia ocena RPM poszkodowanych: 5.8508
# Średni czas symulacji: 223.07
# Średni czas pomocy: 108.99650000000005
# Średnia wartość funkcji celu: -122.42299999999999
# Wartość funkcji celu dla średnich wartości: -122.42325000000002
