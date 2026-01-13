import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json
import csv

# 如果matplotlib可用，导入它
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("警告: matplotlib未安装，将跳过图表生成")

class CCTPAnalyzer:
    def __init__(self, transfers_file="all_chains_transfers.csv", gas_file="all_chains_gas.csv"):
        """初始化分析器"""
        self.transfers_file = transfers_file
        self.gas_file = gas_file
        self.transfers_df = None
        self.gas_df = None
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        try:
            self.transfers_df = pd.read_csv(self.transfers_file)
            self.gas_df = pd.read_csv(self.gas_file)
            
            # 转换时间戳为日期
            self.transfers_df['date'] = pd.to_datetime(self.transfers_df['blockTimestamp'], unit='s').dt.date
            self.gas_df['date'] = pd.to_datetime(self.gas_df['blockTimestamp'], unit='s').dt.date
            
            print(f"成功加载数据:")
            print(f"- 转账记录: {len(self.transfers_df):,} 条")
            print(f"- Gas费用记录: {len(self.gas_df):,} 条")
            print(f"- 数据时间范围: {self.transfers_df['date'].min()} 到 {self.transfers_df['date'].max()}")
            
        except Exception as e:
            print(f"加载数据失败: {e}")
            raise
    
    def basic_statistics(self):
        """任务1: 基础统计分析"""
        print("\n" + "="*60)
        print("任务 1: 基础统计分析")
        print("="*60)
        
        # 总转账统计
        total_transfers = len(self.transfers_df)
        total_amount_usd = self.transfers_df['amount_usd'].sum()
        average_amount = self.transfers_df['amount_usd'].mean()
        
        # 手续费统计（按链分别统计，因为单位不同）
        fee_stats = self.gas_df.groupby(['chain', 'native_symbol']).agg({
            'fee_native': 'sum',
            'fee_gas_native': 'sum'
        }).reset_index()
        
        print(f"1. 总转账统计:")
        print(f"   - 总转账次数: {total_transfers:,}")
        print(f"   - 总转账金额: ${total_amount_usd:,.2f}")
        print(f"   - 平均单笔转账金额: ${average_amount:,.2f}")
        
        print(f"\n2. 手续费收入统计 (按链分别统计):")
        for _, row in fee_stats.iterrows():
            total_fee = row['fee_native'] + row['fee_gas_native']
            print(f"   - {row['chain']}: {total_fee:.8f} {row['native_symbol']} (fee: {row['fee_native']:.8f} + gas: {row['fee_gas_native']:.8f})")
        
        # 按链统计
        chain_stats = self.transfers_df.groupby('chain').agg({
            'amount_usd': ['count', 'sum', 'mean']
        }).round(2)
        chain_stats.columns = ['转账次数', '总金额(USD)', '平均金额(USD)']
        
        print(f"\n3. 各链统计:")
        print(chain_stats.to_string())
        
        return {
            'total_transfers': total_transfers,
            'total_amount_usd': total_amount_usd,
            'average_amount': average_amount,
            'chain_stats': chain_stats,
            'fee_stats': fee_stats
        }
    
    def user_analysis(self):
        """用户维度分析"""
        print("\n" + "="*60)
        print("任务 1: 用户维度分析")
        print("="*60)
        
        # 检查是否有用户地址数据
        if 'from' not in self.transfers_df.columns:
            print("警告: 数据中缺少用户地址信息，无法进行用户维度分析")
            print("请重新运行数据收集脚本以获取完整数据")
            return None
        
        # 按用户统计转账次数
        user_transfer_counts = self.transfers_df.groupby('from').agg({
            'amount_usd': ['count', 'sum', 'mean']
        }).round(2)
        user_transfer_counts.columns = ['转账次数', '总金额(USD)', '平均金额(USD)']
        user_transfer_counts = user_transfer_counts.sort_values('转账次数', ascending=False)
        
        # 转账次数最多的前10个地址
        top_10_by_count = user_transfer_counts.head(10)
        
        # 转账金额最大的前10个地址
        top_10_by_amount = user_transfer_counts.sort_values('总金额(USD)', ascending=False).head(10)
        
        # 计算平均每个用户的转账次数
        total_users = len(user_transfer_counts)
        avg_transfers_per_user = user_transfer_counts['转账次数'].mean()
        
        print(f"1. 用户统计概览:")
        print(f"   - 总用户数: {total_users:,}")
        print(f"   - 平均每个用户转账次数: {avg_transfers_per_user:.2f}")
        
        print(f"\n2. 转账次数最多的前10个地址:")
        for i, (address, data) in enumerate(top_10_by_count.iterrows(), 1):
            print(f"   {i:2d}. {address[:10]}...{address[-8:]}: {data['转账次数']:.0f}次, ${data['总金额(USD)']:,.2f}")
        
        print(f"\n3. 转账金额最大的前10个地址:")
        for i, (address, data) in enumerate(top_10_by_amount.iterrows(), 1):
            print(f"   {i:2d}. {address[:10]}...{address[-8:]}: ${data['总金额(USD)']:,.2f}, {data['转账次数']:.0f}次")
        
        # 用户行为分析
        single_transfer_users = len(user_transfer_counts[user_transfer_counts['转账次数'] == 1])
        frequent_users = len(user_transfer_counts[user_transfer_counts['转账次数'] >= 10])
        whale_users = len(user_transfer_counts[user_transfer_counts['总金额(USD)'] >= 100000])
        
        print(f"\n4. 用户行为分析:")
        print(f"   - 只转账1次的用户: {single_transfer_users:,} ({single_transfer_users/total_users*100:.1f}%)")
        print(f"   - 转账≥10次的活跃用户: {frequent_users:,} ({frequent_users/total_users*100:.1f}%)")
        print(f"   - 总金额≥$100K的大户: {whale_users:,} ({whale_users/total_users*100:.1f}%)")
        
        return {
            'total_users': total_users,
            'avg_transfers_per_user': avg_transfers_per_user,
            'top_10_by_count': top_10_by_count,
            'top_10_by_amount': top_10_by_amount,
            'user_stats': user_transfer_counts,
            'single_transfer_users': single_transfer_users,
            'frequent_users': frequent_users,
            'whale_users': whale_users
        }
    
    def time_analysis(self):
        """时间维度分析"""
        print("\n" + "="*60)
        print("任务 1: 时间维度分析")
        print("="*60)
        
        # 按日期统计
        daily_stats = self.transfers_df.groupby('date').agg({
            'amount_usd': ['count', 'sum', 'mean']
        }).round(2)
        daily_stats.columns = ['转账次数', '总金额(USD)', '平均金额(USD)']
        daily_stats = daily_stats.sort_index()
        
        # 找出最活跃的日期
        most_active_date = daily_stats['转账次数'].idxmax()
        most_active_count = daily_stats.loc[most_active_date, '转账次数']
        
        highest_volume_date = daily_stats['总金额(USD)'].idxmax()
        highest_volume_amount = daily_stats.loc[highest_volume_date, '总金额(USD)']
        
        # 计算日均数据
        avg_daily_transfers = daily_stats['转账次数'].mean()
        avg_daily_amount = daily_stats['总金额(USD)'].mean()
        
        print(f"1. 时间统计:")
        print(f"   - 数据天数: {len(daily_stats)} 天")
        print(f"   - 转账最活跃日期: {most_active_date} ({most_active_count:.0f} 笔)")
        print(f"   - 金额最高日期: {highest_volume_date} (${highest_volume_amount:,.2f})")
        print(f"   - 日均转账次数: {avg_daily_transfers:.1f} 笔")
        print(f"   - 日均转账金额: ${avg_daily_amount:,.2f}")
        
        print(f"\n2. 最近10天统计:")
        print(daily_stats.tail(10).to_string())
        
        # 按月统计
        monthly_stats = self.transfers_df.copy()
        monthly_stats['month'] = pd.to_datetime(monthly_stats['blockTimestamp'], unit='s').dt.to_period('M')
        monthly_summary = monthly_stats.groupby('month').agg({
            'amount_usd': ['count', 'sum', 'mean']
        }).round(2)
        monthly_summary.columns = ['转账次数', '总金额(USD)', '平均金额(USD)']
        
        print(f"\n3. 按月统计:")
        print(monthly_summary.to_string())
        
        return {
            'daily_stats': daily_stats,
            'most_active_date': most_active_date,
            'most_active_count': most_active_count,
            'highest_volume_date': highest_volume_date,
            'highest_volume_amount': highest_volume_amount,
            'avg_daily_transfers': avg_daily_transfers,
            'avg_daily_amount': avg_daily_amount,
            'monthly_stats': monthly_summary
        }
    
    def export_daily_stats(self, filename="daily_transfer_stats.csv"):
        """导出每日转账统计表"""
        daily_stats = self.transfers_df.groupby('date').agg({
            'amount_usd': ['count', 'sum', 'mean']
        }).round(6)
        daily_stats.columns = ['transfer_count', 'total_amount_usd', 'average_amount_usd']
        daily_stats = daily_stats.reset_index()
        daily_stats['date'] = daily_stats['date'].astype(str)
        
        daily_stats.to_csv(filename, index=False)
        print(f"已导出每日统计表: {filename}")
        return daily_stats
    
    def export_user_rankings(self, filename="active_users_ranking.csv"):
        """导出活跃用户排行榜"""
        if 'from' not in self.transfers_df.columns:
            print("警告: 数据中缺少用户地址信息，无法导出用户排行榜")
            return None
            
        user_stats = self.transfers_df.groupby('from').agg({
            'amount_usd': ['count', 'sum', 'mean']
        }).round(6)
        user_stats.columns = ['transfer_count', 'total_amount_usd', 'average_amount_usd']
        user_stats = user_stats.reset_index()
        user_stats = user_stats.sort_values('transfer_count', ascending=False)
        
        user_stats.to_csv(filename, index=False)
        print(f"已导出用户排行榜: {filename}")
        return user_stats
    
    def export_summary_report(self, filename="analysis_summary.json"):
        """导出分析摘要报告"""
        basic_stats = self.basic_statistics()
        time_stats = self.time_analysis()
        
        summary = {
            "report_generated_at": datetime.now().isoformat(),
            "data_period": {
                "start_date": str(self.transfers_df['date'].min()),
                "end_date": str(self.transfers_df['date'].max()),
                "total_days": len(self.transfers_df['date'].unique())
            },
            "overall_statistics": {
                "total_transfers": int(basic_stats['total_transfers']),
                "total_amount_usd": float(basic_stats['total_amount_usd']),
                "average_amount_usd": float(basic_stats['average_amount']),
                "chains_covered": list(self.transfers_df['chain'].unique())
            },
            "time_analysis": {
                "most_active_date": str(time_stats['most_active_date']),
                "most_active_transfers": int(time_stats['most_active_count']),
                "highest_volume_date": str(time_stats['highest_volume_date']),
                "highest_volume_amount": float(time_stats['highest_volume_amount']),
                "daily_average_transfers": float(time_stats['avg_daily_transfers']),
                "daily_average_amount": float(time_stats['avg_daily_amount'])
            },
            "chain_breakdown": {}
        }
        
        # 添加各链详细统计
        for chain in self.transfers_df['chain'].unique():
            chain_data = self.transfers_df[self.transfers_df['chain'] == chain]
            summary["chain_breakdown"][chain] = {
                "total_transfers": len(chain_data),
                "total_amount_usd": float(chain_data['amount_usd'].sum()),
                "average_amount_usd": float(chain_data['amount_usd'].mean()),
                "percentage_of_total_transfers": float(len(chain_data) / len(self.transfers_df) * 100),
                "percentage_of_total_volume": float(chain_data['amount_usd'].sum() / self.transfers_df['amount_usd'].sum() * 100)
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"已导出分析摘要: {filename}")
        return summary
    
    def generate_charts(self):
        """生成图表"""
        if not HAS_MATPLOTLIB:
            print("跳过图表生成 (matplotlib未安装)")
            return
            
        try:
            # 1. 各链转账次数分布
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 2, 1)
            chain_counts = self.transfers_df['chain'].value_counts()
            plt.pie(chain_counts.values, labels=chain_counts.index, autopct='%1.1f%%')
            plt.title('各链转账次数分布')
            
            # 2. 各链转账金额分布
            plt.subplot(2, 2, 2)
            chain_amounts = self.transfers_df.groupby('chain')['amount_usd'].sum()
            plt.pie(chain_amounts.values, labels=chain_amounts.index, autopct='%1.1f%%')
            plt.title('各链转账金额分布')
            
            # 3. 每日转账趋势
            plt.subplot(2, 2, 3)
            daily_counts = self.transfers_df.groupby('date').size()
            plt.plot(daily_counts.index, daily_counts.values)
            plt.title('每日转账次数趋势')
            plt.xticks(rotation=45)
            
            # 4. 转账金额分布
            plt.subplot(2, 2, 4)
            plt.hist(self.transfers_df['amount_usd'], bins=50, alpha=0.7)
            plt.title('转账金额分布')
            plt.xlabel('金额 (USD)')
            plt.ylabel('频次')
            plt.yscale('log')
            
            plt.tight_layout()
            plt.savefig('cctp_analysis_charts.png', dpi=300, bbox_inches='tight')
            print("已生成图表: cctp_analysis_charts.png")
            
        except Exception as e:
            print(f"生成图表时出错: {e}")
    
    def run_complete_analysis(self):
        """运行完整分析"""
        print("开始 CCTP Agent 数据分析...")
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 基础统计
        basic_stats = self.basic_statistics()
        
        # 时间分析
        time_stats = self.time_analysis()
        
        # 用户分析
        user_stats = self.user_analysis()
        
        # 导出数据
        print("\n" + "="*60)
        print("任务 2: 数据导出")
        print("="*60)
        
        daily_stats = self.export_daily_stats()
        user_rankings = self.export_user_rankings()
        summary = self.export_summary_report()
        
        # 生成图表
        print("\n生成可视化图表...")
        self.generate_charts()
        
        print("\n" + "="*60)
        print("分析完成！")
        print("="*60)
        print("生成的文件:")
        print("- daily_transfer_stats.csv (每日转账统计)")
        print("- active_users_ranking.csv (活跃用户排行榜)")
        print("- analysis_summary.json (分析摘要)")
        if HAS_MATPLOTLIB:
            print("- cctp_analysis_charts.png (图表)")
        else:
            print("- 图表生成已跳过 (需要安装matplotlib)")
        
        return {
            'basic_stats': basic_stats,
            'time_stats': time_stats,
            'user_stats': user_stats,
            'daily_stats': daily_stats,
            'user_rankings': user_rankings,
            'summary': summary
        }

if __name__ == "__main__":
    # 运行分析
    analyzer = CCTPAnalyzer()
    results = analyzer.run_complete_analysis()