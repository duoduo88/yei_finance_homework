# CCTP Agent Subgraph 查询语句

## 概述

本文档包含了用于查询 Yei CCTP Agent 数据的 GraphQL 查询语句和使用示例。

## Subgraph 端点

### 各链端点地址

```
ETH:     https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-mainnet/v0.0.13/gn
BASE:    https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-base/v0.0.13/gn
AVAX:    https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-avalanche/v0.0.13/gn
ARB:     https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-arbitrum-one/v0.0.13/gn
POLYGON: https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-matic/v0.0.13/gn
OP:      https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-optimism/v0.0.13/gn
```

## 核心查询语句

### 1. 基础数据查询

获取转账记录和手续费信息：

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

### 2. 日活跃用户统计（以UTC+0时间2024-10-12到2024-10-13为例）
```graphql
{
  depositForBurns(
    first: 1000
    where: {
      blockTimestamp_gte: "1728691200"
      blockTimestamp_lt: "1728777600"
    }
  ) {
    from
  }
}
```

### 3. 大额转账监控
```graphql
{
  depositForBurns(
    first: 100
    where: {
      amount_gte: "100000000000"
    }
    orderBy: blockTimestamp
    orderDirection: desc
  ) {
    id
    from
    amount
    blockTimestamp
  }
}
```

### 4. 手续费统计
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

