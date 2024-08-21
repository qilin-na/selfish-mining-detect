import os
import csv
from flask import Flask, request, jsonify
from tqdm import tqdm
from datetime import datetime

app = Flask(__name__)


def merge_tsv_file(folder_path, output_name, file_path, start_date=None, end_date=None):
    with open(file_path, 'w') as f:
        f.truncate(0)

    write_count = 0
    for filename in sorted(os.listdir(folder_path)):
        # 如果文件名包含日期，解析日期并进行过滤
        if start_date and end_date:
            try:
                file_date_str = filename.split('_')[-1].replace('.tsv', '')
                file_date = datetime.strptime(file_date_str, "%Y%m%d")
                if not (start_date <= file_date <= end_date):
                    continue
            except ValueError:
                continue

        if filename != output_name:
            if filename.endswith(".tsv"):
                with open(os.path.join(folder_path, filename), 'r') as file:
                    lines = file.readlines()
                with open(file_path, 'a') as f:
                    if write_count == 0:
                        f.writelines(lines)
                    else:
                        f.writelines(lines[1:])
                    f.write('\n')
                    write_count += len(lines) - 1 if write_count > 0 else len(lines)

    # 如果没有任何数据被写入，抛出异常或返回提示
    if write_count == 0:
        raise ValueError("No data was found for the given date range. Please check the date range and try again.")


def filter_tsv_file(file_path, block_count):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if len(lines) == 0:
        raise ValueError("The merged file is empty, filtering cannot be performed.")

    # 过滤区块数量
    filtered_lines = lines[:block_count + 1]  # 保留前block_count+1行 (包含头部)

    with open(file_path, 'w') as file:
        file.writelines(filtered_lines)


def read_tsv_file(file_path):
    miner_id_dict = {}
    blockchain_length = 0
    miner_index = 0

    with open(file_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        for line_id, line in enumerate(reader):
            if line_id == 0:
                for i in range(len(line)):
                    if line[i] == 'miner':
                        miner_index = i
                        continue
            elif len(line) == 0:
                continue
            elif line[miner_index] in miner_id_dict.keys():
                miner_id_dict[line[miner_index]] = miner_id_dict[line[miner_index]] + ' ' + line[0]
            else:
                miner_id_dict[line[miner_index]] = line[0]
            blockchain_length = line_id

    if blockchain_length == 0:
        raise ValueError("The TSV file is empty or does not contain valid data.")

    return blockchain_length, len(miner_id_dict), miner_id_dict


def get_miner_list_and_consecutive_blocks_dict(blockchain_len, miner_id_dict):
    miner_list = []
    consecutive_blocks_dict = {}
    hashing_power_dict = {}

    for key, values in miner_id_dict.items():
        miner_list.append(key)
        consecutive_blocks = 0
        value_list = values.split()
        values_cnt = len(value_list)
        miner_id_list = []
        for i in range(values_cnt):
            miner_id_list.append(int(value_list[i]))
            if i != 0 and miner_id_list[i] == miner_id_list[i - 1] + 1:
                consecutive_blocks += 1
        consecutive_blocks_dict[key] = consecutive_blocks
        hashing_power_dict[key] = values_cnt / blockchain_len

    return miner_list, consecutive_blocks_dict, hashing_power_dict


def prob_distribution(i, x, t, miner_list, hashing_power_dict):
    dp = {}

    stack = [(i, x, t)]
    pending = {}

    while stack:
        current_i, current_x, current_t = stack.pop()

        if (current_i, current_x, current_t) in dp:
            continue

        if current_x == 0 and current_t < 2:
            dp[(current_i, current_x, current_t)] = 1
        elif current_x == current_t - 1:
            dp[(current_i, current_x, current_t)] = hashing_power_dict[miner_list[current_i]] ** current_t
        elif current_x > 0 and current_x == current_t - 2:
            dp[(current_i, current_x, current_t)] = 2 * (1 - hashing_power_dict[miner_list[current_i]]) \
                                                    * (hashing_power_dict[miner_list[current_i]] ** (current_t - 1))
        elif 0 <= current_x < current_t - 2:
            if (current_i, current_x, current_t) not in pending:
                pending[(current_i, current_x, current_t)] = (0, 1)
                stack.append((current_i, current_x, current_t))

                for j in range(1, current_x + 3):
                    next_x = current_x - max(0, j - 2)
                    next_t = current_t - j
                    stack.append((current_i, next_x, next_t))
            else:
                result, start_j = pending[(current_i, current_x, current_t)]
                for j in range(start_j, current_x + 3):
                    next_x = current_x - max(0, j - 2)
                    next_t = current_t - j
                    if (current_i, next_x, next_t) in dp:
                        subproblem_result = dp[(current_i, next_x, next_t)]
                        result += (hashing_power_dict[miner_list[current_i]] ** (j - 1)) \
                                  * (1 - hashing_power_dict[miner_list[current_i]]) * subproblem_result
                        pending[(current_i, current_x, current_t)] = (result, j + 1)
                    else:
                        stack.append((current_i, current_x, current_t))
                        break
                else:
                    dp[(current_i, current_x, current_t)] = result
                    del pending[(current_i, current_x, current_t)]
        else:
            dp[(current_i, current_x, current_t)] = 0

    return dp.get((i, x, t), -1)


def p_value(t, miner_list, consecutive_blocks_dict, hashing_power_dict):
    disordered_p_list = []
    ordered_p_dict = {}
    corrected_value_list = []
    total_iterations = sum(consecutive_blocks_dict[miner_list[i]] for i in range(len(miner_list)))

    for i in range(len(miner_list)):
        corrected_value = 0
        for j in range(5):
            prob = prob_distribution(i, j, 5, miner_list, hashing_power_dict)
            corrected_value += prob
        corrected_value_list.append(corrected_value)

    with tqdm(total=total_iterations, desc="Detecting progress") as pbar:
        for i in range(len(miner_list)):
            p = 0
            for x in range(consecutive_blocks_dict[miner_list[i]]):
                p += prob_distribution(i, x, t, miner_list, hashing_power_dict)
                pbar.update(1)
            disordered_p_list.append(1 - p / corrected_value_list[i])

    for k in range(len(miner_list)):
        min_p_idx = 0
        for i in range(len(miner_list)):
            if disordered_p_list[i] < disordered_p_list[min_p_idx]:
                min_p_idx = i
        ordered_p_dict[miner_list[min_p_idx]] = disordered_p_list[min_p_idx]
        disordered_p_list[min_p_idx] = 2

    return ordered_p_dict


def find_attackers(ordered_p_dict, miner_list):
    ordered_p_list = [ordered_p_dict[key] for key in ordered_p_dict]
    attackers_list = []
    i = 0
    for key in ordered_p_dict:
        if ordered_p_list[i] < 0.05 * (i + 1) / len(miner_list):
            attackers_list.append(key)
        i += 1

    if len(attackers_list) == 0:
        return "There is no selfish miner."
    else:
        return f"Selfish miners: {attackers_list}"


@app.route('/detect', methods=['POST'])
def detect_selfish_miners():
    data = request.json
    chain_choice = data.get('chain_choice')
    date_range = data.get('date_range')

    # 根据chain_choice设置默认的block_count
    if chain_choice == 1:
        folder_path = 'data/BTC/blocks_copy/'
        default_block_count = 1000  # BTC的默认最大区块数
    elif chain_choice == 2:
        folder_path = 'data/BCH/blocks/'
        default_block_count = 1000  # BCH的默认最大区块数
    elif chain_choice == 3:
        folder_path = 'data/ETH/blocks/'
        default_block_count = 700  # ETH的默认最大区块数
    elif chain_choice == 4:
        folder_path = 'data/LTC/blocks/'
        default_block_count = 700  # LTC的默认最大区块数
    else:
        return jsonify({"error": "Invalid input"}), 400

    # 使用链选择的默认block_count, 如果未指定block_count的话
    block_count = data.get('block_count', default_block_count)

    # 解析日期范围
    start_date = end_date = None
    if date_range:
        try:
            start_str, end_str = date_range.split('-')
            start_date = datetime.strptime(start_str.strip(), "%Y年%m月%d日")
            end_date = datetime.strptime(end_str.strip(), "%Y年%m月%d日")
        except ValueError:
            return jsonify({"error": "Invalid date range format"}), 400

    output_name = 'All_blocks.tsv'
    file_path = os.path.join(folder_path, output_name)

    # Step 1: 合并tsv文件
    merge_tsv_file(folder_path, output_name, file_path, start_date, end_date)

    # Step 2: 如果有指定区块数量，过滤合并文件
    filter_tsv_file(file_path, block_count)

    # Step 3: 读取区块信息, 生成矿池-区块id列表 字典
    blockchain_len, miner_cnt, miner_id_dict = read_tsv_file(file_path)

    # Step 4: 计算各矿池连续发掘区块的数目, 形成矿池列表和 矿池-连续区块数 字典与 矿池-哈希算力 字典
    miner_list, consecutive_blocks_dict, hashing_power_dict = get_miner_list_and_consecutive_blocks_dict(blockchain_len,
                                                                                                         miner_id_dict)

    # Step 5: 计算加权p值
    ordered_p_dict = p_value(blockchain_len, miner_list, consecutive_blocks_dict, hashing_power_dict)

    # Step 6: 发掘自私攻击者
    result = find_attackers(ordered_p_dict, miner_list)

    return jsonify({"result": result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
