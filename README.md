### 操作指南: 使用 `selfish-mining-detect` 程序

该指南介绍如何安装、部署和使用 `selfish-mining-detect` 程序，程序已打包为 Docker 镜像并上传到 Docker Hub。

---

### 1. 拉取 Docker 镜像

在使用该程序之前，您需要从 Docker Hub 拉取 Docker 镜像：

```bash
docker pull linking86/selfish-mining-detect:latest
```

---

### 2. 运行 Docker 容器

使用以下命令运行容器：

```bash
docker run -d -p 5000:5000 linking86/selfish-mining-detect:latest
```

这将在本地的 5000 端口启动 Flask 应用程序。

---

### 3. 使用 API 进行自私挖矿检测

API 通过 POST 请求与 `/detect` 路由进行交互。您可以使用 `curl` 或其他 HTTP 客户端工具（如 Postman，Apifox等）发送请求。

#### 请求格式

**请求URL：**
```
http://<server-ip>:5000/detect
```

**请求方法：**
- POST

**请求头：**
- Content-Type: application/json

**请求体（JSON格式）：**
```json
{
  "chain_choice": <int>,
  "date_range": "<start_date> - <end_date>",
  "block_count": <int>
}
```

**参数说明：**
- `chain_choice`: 必选，选择区块链类型
  - 1: 比特币（BTC）
  - 2: 比特币现金（BCH）
  - 3: 以太坊（ETH）
  - 4: 莱特币（LTC）
- `date_range`: 可选，日期范围，格式为 `"YYYY年MM月DD日 - YYYY年MM月DD日"`，用于筛选指定日期范围内的区块。
- `block_count`: 可选，最大区块总数。如果未指定，将使用各区块链的默认最大值（BTC和BCH为1000，ETH和LTC为700）。

#### 示例请求

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"chain_choice\":1, \"date_range\":\"2024年08月01日-2024年08月07日\", \"block_count\":500}"  http://localhost:5000/detect
```

---

### 4. 返回结果

API 会返回 JSON 格式的结果，说明是否检测到自私挖矿行为。

**成功返回：**
```json
{
  "result": "Selfish miners: ['miner1', 'miner2']"
}
```

**未检测到自私挖矿者：**
```json
{
  "result": "There is no selfish miner."
}
```

---

### 5. 文件结构和说明

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

- **`BTC`/`BCH`/`ETH`/`LTC` 文件夹**：包含相应区块链的区块数据，数据应以 `.tsv` 格式存放在 `blocks` 文件夹内。具体数据格式可参考对应的`example_XXX.tsv`文件；
- 如果要使用指定日期范围功能，文件命名需要以`your_blocks_name_YYYYMMDD.tsv`为规范，详情可参考对应文件夹下的`example_XXX_20240801.tsv`的文件命名。

---


通过以上步骤，您可以顺利地使用 `selfish-mining-detect` 程序检测区块链网络中的自私挖矿行为。