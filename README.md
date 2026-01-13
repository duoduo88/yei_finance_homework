# CCTP Agent 数据分析项目

## 项目概述

本项目旨在完成 Yei CCTP Agent 在六条区块链（ETH、BASE、AVAX、ARB、POLYGON、OP）上的跨链转账数据分析任务。

## 文件结构

```
yei_finance_homework/
├── yei_cctp_export.py          # 数据收集脚本 (查询脚本)
├── yei_cctp_analysis.py        # 数据分析脚本 (数据导出脚本)
├── subgraph_queries.md         # Subgraph 查询语句详细文档
├── homework.md                 # 作业要求
├── README.md                   # 本文件
├── all_chains_transfers.csv    # 转账数据 (17,598条)
├── all_chains_gas.csv          # 手续费数据 (17,598条)
├── daily_transfer_stats.csv    # 每日统计表 (278天)
├── active_users_ranking.csv    # 用户排行榜 (12,455用户)
├── analysis_summary.json       # 分析摘要 (JSON格式)
```

## 核心脚本说明

### 1. 查询脚本 (`yei_cctp_export.py`)

**功能**: 从 Subgraph 查询并收集所有链的原始数据

**使用的 GraphQL 查询**:
```graphql
{
  depositForBurns(first: 1000, skip: 0) {
    id
    from
    amount
    blockTimestamp
  }
  depositForBurnV2S(first: 1000, skip: 0) {
    id
    from
    amount
    fee
    feeForgasOnDestination
    blockTimestamp
  }
}
```

**输出文件**:
- `all_chains_transfers.csv` - 转账主表
- `all_chains_gas.csv` - 手续费表

### 2. 数据导出脚本 (`yei_cctp_analysis.py`)

**功能**: 对收集的数据进行多维度分析并导出结果

**核心分析模块**:

- `basic_statistics()` - 基础统计分析
- `time_analysis()` - 时间维度分析  
- `user_analysis()` - 用户维度分析
- `export_daily_stats()` - 导出每日统计
- `export_user_rankings()` - 导出用户排行榜
- `export_summary_report()` - 导出分析摘要

**输出文件**:

- `daily_transfer_stats.csv` - 每日转账统计表
- `active_users_ranking.csv` - 活跃用户排行榜  
- `analysis_summary.json` - 完整分析摘要

## 运行步骤

### 1. 环境准备

```bash
pip install pandas numpy requests
```

### 2. 数据收集

```bash
python yei_cctp_export.py
```

这将从 Subgraph 获取所有链的数据，生成：
- `all_chains_transfers.csv` - 转账主表
- `all_chains_gas.csv` - 手续费表

### 3. 数据分析

```bash
python yei_cctp_analysis.py
```

这将进行完整的数据分析，生成：
- `daily_transfer_stats.csv` - 每日转账统计
- `active_users_ranking.csv` - 活跃用户排行榜
- `analysis_summary.json` - 分析摘要



## 分析结果摘要

### 总体统计
- **总转账次数**: 17,598 笔
- **总转账金额**: $317,400,233.82
- **平均转账金额**: $18,036.15
- **数据时间范围**: 2024-10-06 至 2025-08-04 (278 天)
- **日均转账次数**: 63.3 笔
- **日均转账金额**: $1,141,727.46

### 链分布
- **最活跃的链**: ARB (5,630 笔, 32.0%)

- **最大金额的链**: AVAX ($181,139,892.13, 57.1%)

- **平均金额最高**: AVAX ($79,447.32)

- **链分布分析**

  | 链名称  | 转账次数 | 占比  | 总金额 (USD)    | 占比  | 平均金额   |
  | ------- | -------- | ----- | --------------- | ----- | ---------- |
  | ETH     | 1,141    | 6.5%  | $62,966,673.89  | 19.8% | $55,185.52 |
  | BASE    | 3,217    | 18.3% | $11,428,598.58  | 3.6%  | $3,552.56  |
  | AVAX    | 2,280    | 13.0% | $181,139,892.13 | 57.1% | $79,447.32 |
  | ARB     | 5,630    | 32.0% | $42,041,955.03  | 13.2% | $7,467.49  |
  | POLYGON | 1,947    | 11.1% | $6,146,961.99   | 1.9%  | $3,157.15  |
  | OP      | 3,383    | 19.2% | $13,676,152.20  | 4.3%  | $4,042.61  |

  **关键发现**:

  - 最活跃的链: ARB (5,630 笔)
  - 最大金额的链: AVAX ($181,139,892.13)

### 用户行为
- **总用户数**: 12,455
- **平均每用户转账**: 1.41 次
- **单次转账用户**: 9,587 (77.0%)
- **用户分层分析**：

  - **一次性用户**: 9,399 (77.5%) 
  - **活跃用户** (≥10次): 35 (0.3%)
  - **大户** (≥$100K): 313 (2.6%) 

- **用户概览**：

  - **总用户数**: 12,135 个地址
  - **平均每用户转账次数**: 1.39 次
  - **用户行为特征**: 77.5% 的用户只转账一次，说明新用户占主导

  **转账次数最多的前10个地址**：

  `0x4a042b8c865e36f09cdac1a3d526970a308802a2`: 99笔, $72.26

  `0x018c3c52c3c08420b4c0cc041cc53f13359031e8`: 74笔, $125.68  

  `0x649fe0bba5098e9ec1cca4aa416c0551e309a568`: 64笔, $56,652,186.15

  `0xcee99d8ab5003cd51fd5ab11771834d5afc02f2d`: 38笔, $21.77

  `0x813511f567d3dc94eabf37f47996d21b07e6b0cd`: 27笔, $2,186,154.38

  `0x51081c5f2442da2d82be9a1882c88d2bdcdbef25`: 21笔, $2,730.48

  `0x4755b51eed2cd9edb35db1dea1018e6363f30e5c`: 20笔, $5.72

  `0x9d890672b5d2431ab23aa0a024cb8c37e5dc1012`: 20笔, $1,108.94

  `0xb2221d4fa904c70830893caafba25c81b498a3bc`: 18笔, $2,229.50

  `0x4e3a9949461384bef2bc09ba4f2539c4c6e4eed4`: 17笔, $933.60

  **转账金额最大的前10个地址**：

  `0x649fe0bba5098e9ec1cca4aa416c0551e309a568`: $56,652,186.15, 64笔

  `0x9177a60658025f8d506fb2686103c21a3c4c6d50`: $11,000,999.83, 12笔

  `0xf83bcdd35dbe0cd43b9989fed6ea690914451eea`: $10,879,554.73, 11笔

  `0x305ef9ded7ddf6614a8d4bb431ede0ff191b0dd0`: $7,999,993.50, 10笔

  `0x391ad775fa5b92c20e455d9b84ac4d476e6532bf`: $7,794,620.63, 13笔

  `0x3368830992fa7e1a290a41897a859b56b1b0999e`: $7,529,446.22, 9笔

  `0x100032ed9ef405648dc3cc71b6d09c63011ea4f5`: $7,335,859.78, 11笔

  `0x7f248eb5802cd54090c9045c25d2e9dcd20d5927`: $6,996,499.81, 7笔

  `0x171c53d55b1bcb725f660677d9e8bad7fd084282`: $6,653,589.21, 14笔

  `0xd4f9ce639ddf663212579514abed27266a5cfe3c`: $6,611,222.29, 10笔

### 时间趋势
- **最活跃日期**: 2025-03-04 (1,730 笔)
- **最高金额日期**: 2025-05-08 ($19,091,074.73)
- **日均转账**: 63.3 笔
- **日均金额**: $1,141,727.46

## 技术实现

### 数据源
- **Subgraph API**: Goldsky 提供的 6 条链 Subgraph 端点
- **查询方式**: GraphQL 查询 `depositForBurns` 和 `depositForBurnV2S` 事件
- **数据处理**: Python pandas 进行数据清洗和分析

### Subgraph 端点
```
ETH:     https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-mainnet/v0.0.13/gn
BASE:    https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-base/v0.0.13/gn
AVAX:    https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-avalanche/v0.0.13/gn
ARB:     https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-arbitrum-one/v0.0.13/gn
POLYGON: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-matic/v0.0.13/gn
OP:      https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-optimism/v0.0.13/gn
```



# 详细的查询语句和使用示例请参考 `subgraph_queries.md` 文件。




