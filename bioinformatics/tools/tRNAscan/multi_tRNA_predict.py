import os
import subprocess
from tqdm import tqdm  # 用于显示进度条
from concurrent.futures import ProcessPoolExecutor


def run_tRNAscan(input_file, output_folder):
    """
    调用 tRNAscan-SE 处理单个文件。

    :param input_file: 输入的 .fna 文件路径
    :param output_folder: 输出结果文件的保存文件夹
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 构建输出文件路径
    output_file = os.path.join(output_folder, "tRNA.out")
    structure_file = os.path.join(output_folder, "rRNA.ss")
    stats_file = os.path.join(output_folder, "tRNA.stats")

    # 检查输出文件是否已经存在
    if os.path.exists(output_file) and os.path.exists(structure_file) and os.path.exists(stats_file):
        print(f"文件已存在，跳过: {input_file}")
        return

    # 构建命令
    command = [
        "/disk2/guo/anaconda3/envs/LLM39/bin/tRNAscan-SE",
        "-o", output_file,
        "-f", structure_file,
        "-m", stats_file,
        input_file
    ]

    # 执行命令
    try:
        subprocess.run(command, check=True)
        print(f"处理完成: {input_file}")
    except subprocess.CalledProcessError as e:
        print(f"处理文件 {input_file} 时出错: {e}")
    except FileNotFoundError:
        print("未找到 tRNAscan-SE，请确保它已安装并在 PATH 中。")


def process_fna_file(fna_file):
    """
    包装单个文件的处理逻辑，用于多进程调用。

    :param fna_file: 输入的 .fna 文件路径
    """
    output_folder = os.path.dirname(fna_file)
    run_tRNAscan(fna_file, output_folder)


def process_all_fna_files(base_folder, num_processes=None):
    """
    遍历指定文件夹，找到所有 .fna 文件并并行运行 tRNAscan-SE。

    :param base_folder: 根文件夹路径
    :param num_processes: 并行进程数，默认为系统 CPU 数量。
    """
    # 收集所有 .fna 文件路径
    fna_files = []
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".fna"):
                fna_files.append(os.path.join(root, file))

    # 使用多进程池处理所有文件
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        with tqdm(total=len(fna_files), desc="Processing files") as pbar:
            futures = [executor.submit(process_fna_file, fna_file) for fna_file in fna_files]
            for future in futures:
                try:
                    future.result()  # 捕获任务中的异常
                except Exception as e:
                    print(f"任务失败: {e}")
                pbar.update()


# 主程序
if __name__ == "__main__":
    # 基础文件夹路径
    base_folder = "/disk1/guo/data/GTDB/gtdb_genomes_reps_r220/database"
    # 指定最大并行进程数（可以设置为 CPU 核心数量，例如 8）
    process_all_fna_files(base_folder, num_processes=24)
