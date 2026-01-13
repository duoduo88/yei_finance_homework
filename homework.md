# CCTP Agent 数据分析作业

## 作业目标

使用 CCTP Agent Subgraph 或链上事件，完成六条不同区块链上的 Yei 专用跨链转账数据分析任务。

## 任务要求

### 任务 1：数据查询与统计（必做）

使用 Subgraph 或直接查询链上事件，完成以下统计：

#### 1. 总转账统计
- 总转账次数
- 总转账金额（美元价值，需转换为可读格式）
- 总手续费收入
- 平均单笔转账金额

#### 2. 时间维度分析
- 按日期统计每日转账次数和金额
- 找出转账最活跃的日期
- 计算日均转账次数和金额

#### 3. 用户维度分析
- 找出转账次数最多的前 10 个地址
- 找出转账金额最大的前 10 个地址
- 计算平均每个用户的转账次数

### 任务 2：数据导出（必做）

将查询结果导出为 CSV 或 JSON 格式，包含：
- 每日转账统计表（日期、次数、总金额、平均金额）
- 活跃用户排行榜（地址、转账次数、总金额）

### 任务 3：数据分析报告（选做，加分项）

基于以上数据，写一份简要分析报告（1-2 页），包括：
- 数据趋势观察
- 用户行为模式
- 发现的问题或异常

## 技术实现方式（二选一）

### 方式 A：使用 Subgraph（推荐）
- 使用已部署的 Subgraph API 
    ETH: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-mainnet/v0.0.13/gn
    BASE: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-base/v0.0.13/gn
    AVAX: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-avalanche/v0.0.13/gn
    ARB: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-arbitrum-one/v0.0.13/gn
    POLYGON: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-matic/v0.0.13/gn
    OP: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-optimism/v0.0.13/gn
- 编写 GraphQL 查询获取数据
- 使用 Python/JavaScript 处理数据并生成报告

### 方式 B：直接查询链上事件
- 使用 EtherScan API 直接查询合约事件
- 獲取各鏈所有 `DepositForBurn` 事件
- 处理并分析事件数据

## 提交要求

1. **代码仓库（GitHub）**
   - 包含查询脚本
   - 包含数据导出脚本
   - 包含 README 说明如何运行

2. **数据文件**
   - 导出的 CSV/JSON 文件
   - 统计结果摘要

3. **分析报告**（如完成任务 3）

## 评估标准

- 代码质量与可读性（30%）
- 数据准确性（30%）
- 查询效率与优化（20%）
- 报告质量（20%，如完成）

## 参考资源

- **Schema 定义**：
```
type DepositForBurn @entity(immutable: true) {
  id: Bytes!
  from: Bytes! # address
  amount: BigInt! # uint256
  fee: BigInt! # uint256
  feeForGasOnDestination: BigInt! # uint256
  mintRecipient: Bytes! # bytes32
  blockNumber: BigInt!
  blockTimestamp: BigInt!
  transactionHash: Bytes!
  logIndex: BigInt!
}

```

## 提示

- 注意金额单位转换（USDC 通常为 6 位小数）
- EtherScan API 不仅针对 ETH 一条链，homework 中出现的链都可以使用
