### 操作指南：使用 selfish-mining-detect 服务检测自私矿工

本指南将帮助您安装、部署和使用自私挖矿检测程序，以检测区块链中的自私矿工。

---

### 1. 环境准备

#### 1.1 安装 Python
首先，确保您的系统上安装了 Python 3.6 或更高版本。可以通过以下命令检查您的 Python 版本：

```bash
python --version
```

#### 1.2 安装依赖包
在终端或命令行中导航到项目文件夹，然后安装所需的 Python 包。使用以下命令安装依赖包：

```bash
pip install -r requirements.txt
```

---

### 2. 代码部署

#### 2.1 获取代码

```bash
git clone https://github.com/qilin-na/selfish-mining-detect.git
```

#### 2.2 运行服务
在终端或命令行中导航到 `app.py` 文件所在的目录，运行以下命令启动 Flask 服务：

```bash
python app.py
```

如果一切正常，您将看到类似于以下的输出：

```
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

此时，服务已启动，并在端口 `5000` 上运行。

---

### 3. 使用服务

#### 3.1 输入格式
要检测自私矿工，您需要向 `/detect` 端点发送一个 `POST` 请求。请求体应为 JSON 格式，并包含以下字段：

- `chain_choice`: 必选，选择区块链类型
  - 1: 比特币（BTC）
  - 2: 比特币现金（BCH）
  - 3: 以太坊（ETH）
  - 4: 莱特币（LTC）
- `date_range`: 可选，日期范围，格式为 `"YYYY年MM月DD日 - YYYY年MM月DD日"`，用于筛选指定日期范围内的区块。
- `block_count`: 可选，最大区块总数。如果未指定，将使用各区块链的默认最大值（BTC和BCH为1000，ETH和LTC为700）。

#### 示例请求

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"chain_choice\":1, \"date_range\":\"2024年08月01日-2024年08月07日\", \"block_count\":950}" http://localhost:5000/detect
```

您也可以使用 Postman 或其他 API 测试工具发送类似请求。

#### 3.2 输出格式
服务器将返回一个包含检测结果的 JSON 响应。响应格式如下：

- **`result`**：字符串，列出检测到的自私矿工或通知没有自私矿工。

例如，可能的响应为：

```json
{
  "result": "Selfish miners: ['Miner1', 'Miner2']"
}
```

或者

```json
{
  "result": "There is no selfish miner."
}
```

---

### 4. 文件结构和说明

确保数据文件按以下结构存放在项目目录中：

```plaintext
project_directory/
│
├── app.py  # 主程序文件
├── data/                       # 数据文件夹
│   ├── BTC/
│   │   └── blocks/
│   ├── BCH/
│   │   └── blocks/
│   └── ETH/
│       └── blocks/
│   └── LTC/
│       └── blocks/
```

- **`BTC`/`BCH`/`ETH`/`LTC` 文件夹**：包含相应区块链的区块数据，数据应以 `.tsv` 格式存放在 `blocks` 文件夹内。具体数据格式可参考对应的`example_XXX.tsv`文件。

---

通过以上步骤，您可以顺利地使用 `selfish-mining-detect` 程序检测区块链网络中的自私挖矿行为。
