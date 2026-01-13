import requests
import time
import csv
from datetime import datetime

# ===================== 配置 =====================
PAGE_SIZE = 1000
DELAY = 2.0  # 防限流延迟（秒），可调大

# 6 个链的端点和 native token 信息
CHAINS = {
    "ETH": {
        "endpoint": "https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-mainnet/v0.0.13/gn",
        "native_symbol": "ETH",
        "decimals": 18
    },
    "BASE": {
        "endpoint": "https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-base/v0.0.13/gn",
        "native_symbol": "ETH",
        "decimals": 18
    },
    "AVAX": {
        "endpoint": "https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-avalanche/v0.0.13/gn",
        "native_symbol": "AVAX",
        "decimals": 18
    },
    "ARB": {
        "endpoint": "https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-arbitrum-one/v0.0.13/gn",
        "native_symbol": "ETH",
        "decimals": 18
    },
    "POLYGON": {
        "endpoint": "https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-matic/v0.0.13/gn",
        "native_symbol": "MATIC",
        "decimals": 18
    },
    "OP": {
        "endpoint": "https://api.goldsky.com/api/public/project_cmgzims7d000c5np28b637r62/subgraphs/yei-cctp-agent-optimism/v0.0.13/gn",
        "native_symbol": "ETH",
        "decimals": 18
    }
}

# ===================== 查询模板 =====================
QUERY_TEMPLATE = """
{
  depositForBurns(first: %d, skip: %d) {
    id
    from
    amount
    blockTimestamp
  }
  depositForBurnV2S(first: %d, skip: %d) {
    id
    from
    amount
    fee
    feeForgasOnDestination
    blockTimestamp
  }
}
"""

def fetch_page(endpoint, skip):
    query = QUERY_TEMPLATE % (PAGE_SIZE, skip, PAGE_SIZE, skip)
    try:
        response = requests.post(endpoint, json={"query": query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL 错误: {data['errors']}")
            return [], []
        
        burns = data.get("data", {}).get("depositForBurns", [])
        burns_v2 = data.get("data", {}).get("depositForBurnV2S", [])
        return burns, burns_v2
    
    except Exception as e:
        print(f"请求失败: {e}")
        return [], []

def process_chain(chain_name, chain_info, all_transfers_records, all_gas_records):
    endpoint = chain_info["endpoint"]
    native_symbol = chain_info["native_symbol"]
    decimals = chain_info["decimals"]
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始处理 {chain_name}...")
    
    total_count = 0
    total_amount_usd = 0.0
    total_fee_native = 0.0
    total_fee_gas_native = 0.0
    
    skip = 0
    page = 1
    
    while True:
        burns, burns_v2 = fetch_page(endpoint, skip)
        
        page_count = len(burns) + len(burns_v2)
        if page_count == 0:
            break
        
        for item in burns + burns_v2:
            total_count += 1
            
            tx_id = item.get('id', '')
            from_address = item.get('from', '')
            timestamp = item.get('blockTimestamp', '')
            
            # amount → USDC
            amount = int(item.get('amount', 0))
            amount_usd = amount / 1_000_000.0
            
            # fee & fee_gas → native token
            # 注意：v1版本的DepositForBurn事件在Subgraph中没有fee字段
            # 只有v2版本的DepositForBurnV2事件才有fee和feeForgasOnDestination字段
            fee_min = int(item.get('fee', 0))
            fee_gas_min = int(item.get('feeForgasOnDestination', 0))
            fee_native = fee_min / (10 ** decimals)
            fee_gas_native = fee_gas_min / (10 ** decimals)
            
            tx_type = "v2" if 'fee' in item else "v1"
            
            # 1. 转账主表记录
            all_transfers_records.append({
                "chain": chain_name,
                "id": tx_id,
                "from": from_address,
                "type": tx_type,
                "amount_usd": amount_usd,
                "blockTimestamp": timestamp
            })
            
            # 2. gas 费用表记录（只保存有费用的行，或全部保存都行，这里全部保存）
            all_gas_records.append({
                "chain": chain_name,
                "id": tx_id,
                "from": from_address,
                "type": tx_type,
                "fee_native": fee_native,
                "fee_gas_native": fee_gas_native,
                "native_symbol": native_symbol,
                "blockTimestamp": timestamp
            })
            
            total_amount_usd += amount_usd
            total_fee_native += fee_native
            total_fee_gas_native += fee_gas_native
        
        print(f" 第 {page} 页 | 本页 {page_count} 条 | 累计 {total_count:,} 条")
        
        if page_count < PAGE_SIZE:
            break
        
        skip += PAGE_SIZE
        page += 1
        time.sleep(DELAY)
    
    average_amount = total_amount_usd / total_count if total_count > 0 else 0
    
    stats = {
        "chain": chain_name,
        "total_transfers": total_count,
        "total_amount_usd": f"${total_amount_usd:,.2f}",
        "total_fee_native": f"{total_fee_native:,.8f}",
        "total_fee_gas_native": f"{total_fee_gas_native:,.8f}",
        "average_amount_usd": f"${average_amount:,.2f}",
        "native_symbol": native_symbol
    }
    
    print(f"{chain_name} 完成！总转账次数: {total_count:,} | 总金额: ${total_amount_usd:,.2f}")
    return stats

def save_transfers_csv(records, filename="all_chains_transfers.csv"):
    if not records:
        return
    fieldnames = ["chain", "id", "from", "type", "amount_usd", "blockTimestamp"]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow({
                "chain": row["chain"],
                "id": row["id"],
                "from": row["from"],
                "type": row["type"],
                "amount_usd": f"{row['amount_usd']:.6f}",
                "blockTimestamp": row["blockTimestamp"]
            })
    print(f"已保存转账主表：{filename} （{len(records):,} 条）")

def save_gas_csv(records, filename="all_chains_gas.csv"):
    if not records:
        return
    fieldnames = ["chain", "id", "from", "type", "fee_native", "fee_gas_native", "native_symbol", "blockTimestamp"]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow({
                "chain": row["chain"],
                "id": row["id"],
                "from": row["from"],
                "type": row["type"],
                "fee_native": f"{row['fee_native']:.12f}",
                "fee_gas_native": f"{row['fee_gas_native']:.12f}",
                "native_symbol": row["native_symbol"],
                "blockTimestamp": row["blockTimestamp"]
            })
    print(f"已保存 gas 费用表：{filename} （{len(records):,} 条）")

def main():
    all_stats = []
    all_transfers_records = []
    all_gas_records = []
    grand_total_transfers = 0
    grand_total_amount = 0.0
    
    for chain_name, chain_info in CHAINS.items():
        stats = process_chain(chain_name, chain_info, all_transfers_records, all_gas_records)
        all_stats.append(stats)
        
        grand_total_transfers += stats["total_transfers"]
        grand_total_amount += float(stats["total_amount_usd"].replace("$", "").replace(",", ""))
    
    # 保存两个指定的 CSV
    save_transfers_csv(all_transfers_records)
    save_gas_csv(all_gas_records)
    
    # 输出统计汇总（保持原样）
    print("\n" + "="*60)
    print("各链统计汇总：")
    print("-"*60)
    for s in all_stats:
        print(f"{s['chain']}:")
        print(f" 总转账次数: {s['total_transfers']:,}")
        print(f" 总金额: {s['total_amount_usd']}")
        print(f" 总手续费 ({s['native_symbol']}): {s['total_fee_native']} (fee) + {s['total_fee_gas_native']} (gas on dest)")
        print(f" 平均单笔: {s['average_amount_usd']}")
        print()
    
    print("="*60)
    print("全链总和统计：")
    print(f"总转账次数: {grand_total_transfers:,}")
    print(f"总金额: ${grand_total_amount:,.2f}")
    print("总手续费: 详见各链统计（不同链 native token 单位不同，无法简单总和）")
    print("  ※ 手续费单位为各链 native token（如 ETH/AVAX/MATIC），非 USD。通常每笔几分钱 ~ 几美元。")
    print(f"平均单笔金额: ${(grand_total_amount / grand_total_transfers if grand_total_transfers > 0 else 0):,.2f}")
    print("="*60)

if __name__ == "__main__":
    main()