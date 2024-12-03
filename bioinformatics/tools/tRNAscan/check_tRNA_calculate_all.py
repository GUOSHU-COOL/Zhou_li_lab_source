import os
import re
from collections import defaultdict
import pickle

def parse_tRNA_stats(file_path, amino_acids, codon_stats, missing_aa_dict):
    """
    解析单个 tRNA.stats 文件，提取每个氨基酸及其 codon 的信息，并记录缺失氨基酸
    """
    stats = {aa: {"total": 0, "codon_counts": []} for aa in amino_acids}
    missing_aa = []

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            # 使用正则提取氨基酸及其对应的计数信息
            match = re.match(r"(\w+)\s+:\s+(\d+)\s+(.*)", line)
            if match:
                aa = match.group(1)  # 氨基酸名称
                total = int(match.group(2))  # 总数
                codons = match.group(3)  # 具体的 Codon 分布
                # 提取 Codon 的计数
                codon_matches = re.findall(r"(\w+): (\d+)", codons)
                codon_counts = []
                for codon, count in codon_matches:
                    count = int(count)
                    codon_counts.append(count)
                    codon_stats[codon] += count  # 记录 codon 的全局出现次数
                if aa in stats:
                    stats[aa]["total"] += total
                    stats[aa]["codon_counts"].extend(codon_counts)

    # 统计缺失氨基酸
    for aa in amino_acids:
        if stats[aa]["total"] == 0:
            missing_aa.append(aa)

    if missing_aa:
        missing_aa_dict[file_path] = missing_aa

    return stats


def calculate_codon_frequencies(codon_stats):
    """
    根据 codon_stats 计算 codon 的总频率
    """
    total_codons = sum(codon_stats.values())
    codon_frequencies = {codon: count / total_codons for codon, count in codon_stats.items()}
    return codon_frequencies


def process_directory(directory_path, amino_acids):
    """
    遍历目录中的所有 tRNA.stats 文件，统计氨基酸和 codon 的出现次数，记录缺失氨基酸信息
    """
    all_stats = defaultdict(lambda: {"total": 0, "codon_counts": []})
    codon_stats = defaultdict(int)  # 记录 codon 的全局统计
    missing_aa_dict = {}  # 记录缺失氨基酸的文件和对应的氨基酸种类
    total_files = 0
    missing_files_count = 0
    total_missing_aa_count = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file == "tRNA.stats":
                file_path = os.path.join(root, file)
                print(f"处理文件: {file_path}")
                total_files += 1
                stats = parse_tRNA_stats(file_path, amino_acids, codon_stats, missing_aa_dict)

                # 统计缺失氨基酸的数量
                if file_path in missing_aa_dict:
                    missing_files_count += 1
                    total_missing_aa_count += len(missing_aa_dict[file_path])

                # 累加所有文件的统计信息
                for aa in amino_acids:
                    all_stats[aa]["total"] += stats[aa]["total"]
                    all_stats[aa]["codon_counts"].extend(stats[aa]["codon_counts"])

    avg_missing_aa = total_missing_aa_count / total_files if total_files > 0 else 0
    return all_stats, codon_stats, total_files, missing_files_count, avg_missing_aa, missing_aa_dict
def save_missing_aa_dict_pickle(missing_aa_dict, output_path):
    """
    将缺失氨基酸的字典存储为 pickle 文件
    """
    with open(output_path, 'wb') as f:
        pickle.dump(missing_aa_dict, f)
    print(f"Missing amino acids dictionary saved to {output_path}")

def main():
    # 输入文件夹路径
    directory_path = "/disk1/guo/data/GTDB/gtdb_genomes_reps_r220/database/"  # 替换为你的目录路径

    # 定义常见氨基酸列表
    amino_acids = [
        "Ala", "Gly", "Pro", "Thr", "Val", "Ser", "Arg", "Leu",
        "Phe", "Asn", "Lys", "Asp", "Glu", "His", "Gln", "Ile",
        "Met", "Tyr", "Cys", "Trp",
    ]

    # 处理目录
    results = process_directory(directory_path, amino_acids)
    all_stats, codon_stats, total_files, missing_files_count, avg_missing_aa, missing_aa_dict = results

    # 计算 codon 频率
    codon_frequencies = calculate_codon_frequencies(codon_stats)

    # 输出结果
    print(f"\n处理的文件总数: {total_files}")
    print(f"缺失氨基酸的文件数: {missing_files_count}")
    print(f"平均每个文件缺失氨基酸的数量: {avg_missing_aa:.2f}")

    # print("\n缺失氨基酸的文件和对应缺失的氨基酸种类：")
    # for file, missing_aas in missing_aa_dict.items():
    #     print(f"{file}: {', '.join(missing_aas)}")
    output_path = "/nas/guo/results/pretrain_evo/process_pretrain_data/tRNA_info.pkl"
    save_missing_aa_dict_pickle(missing_aa_dict, output_path)
    print("\n所有文件中 Codon 的频率：")
    for codon, frequency in sorted(codon_frequencies.items(), key=lambda x: x[1], reverse=True):
        print(f"{codon}: {frequency:.4f}")


if __name__ == "__main__":
    main()
"""
处理的文件总数: 113104
缺失氨基酸的文件数: 75392
平均每个文件缺失氨基酸的数量: 2.29
Missing amino acids dictionary saved to /nas/guo/results/pretrain_evo/process_pretrain_data/tRNA_info.pkl

所有文件中 Codon 的频率：
CAT: 0.0716
GCC: 0.0320
GTC: 0.0304
TTC: 0.0295
GTT: 0.0281
TAC: 0.0280
TTT: 0.0278
TTG: 0.0259
GAA: 0.0248
TGG: 0.0248
TGT: 0.0247
TCC: 0.0242
TAG: 0.0239
GTA: 0.0239
GTG: 0.0237
GCA: 0.0234
ACG: 0.0233
TGA: 0.0233
TAA: 0.0230
CAA: 0.0228
TCT: 0.0224
GCT: 0.0219
CCA: 0.0218
GGT: 0.0211
GGA: 0.0208
GGC: 0.0207
CCT: 0.0207
GAC: 0.0205
CAG: 0.0203
GAG: 0.0196
CCG: 0.0189
CGT: 0.0183
CTT: 0.0180
TGC: 0.0179
GGG: 0.0178
GAT: 0.0174
CGA: 0.0167
CCC: 0.0161
CTG: 0.0160
CGG: 0.0160
CTC: 0.0152
CAC: 0.0129
CGC: 0.0123
TCG: 0.0077
GCG: 0.0033
AAG: 0.0021
TAT: 0.0015
TCA: 0.0008
AGG: 0.0007
TTA: 0.0002
AGT: 0.0002
ACT: 0.0002
AAA: 0.0001
CTA: 0.0001
AAT: 0.0001
ATT: 0.0001
AGC: 0.0001
AAC: 0.0001
ATC: 0.0001
ACC: 0.0001
AGA: 0.0001
ACA: 0.0001
ATG: 0.0001
ATA: 0.0001
"""