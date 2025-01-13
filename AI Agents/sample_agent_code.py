import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Data
issue_data = {
	'Issue Type': ['API Issue', 'Login Issue', 'Report Generation', 'Data Import', 'Feature Request', 'Billing Issue', 'UI Bug'],
    'Frequency': [10, 10, 8, 10, 8, 12, 8]
}
priority_data = {
	'Issue Type': ['API Issue', 'Login Issue', 'Report Generation', 'Data Import', 'Feature Request', 'Billing Issue', 'UI Bug'],
    'High': [5, 4, 3, 4, 3, 5, 3],
    'Medium': [3, 2, 2, 4, 3, 5, 3],
    'Low': [2, 3, 3, 2, 2, 2, 2],
    'Critical': [2, 1, 0, 0, 2, 3, 2]
}
agent_performance_data = {
	'Agent ID': ['A001', 'A002', 'A003', 'A004', 'A005'],
    'Total Tickets': [10, 10, 10, 10, 10],
    'Average Response Time (mins)': [134.9, 117.9, 147.6, 137.5, 140.5],
    'Average Resolution Time (mins)': [813.6, 770.3, 735.4, 650.9, 753.1],
    'Average Satisfaction Rating': [2.4, 3.5, 2.6, 3.3, 3.1]
}
customer_satisfaction_data = {
	'Month': ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    'Average Satisfaction Rating': [2.8, 3.1, 2.8, 2.9, 3.0, 3.2, 3.0]
}

# Convert to DataFrames
issue_df = pd.DataFrame(issue_data)
priority_df = pd.DataFrame(priority_data)
agent_performance_df = pd.DataFrame(agent_performance_data)
customer_satisfaction_df = pd.DataFrame(customer_satisfaction_data)

# Issue Distribution
plt.figure(figsize=(10, 6))
plt.pie(issue_df['Frequency'], labels=issue_df['Issue Type'], autopct='%1.1f%%', startangle=140)
plt.title('Issue Distribution')
plt.savefig('issue_distribution.png')
plt.close()

# Priority Levels
priority_df_melted = priority_df.melt(id_vars=['Issue Type'], var_name='Priority', value_name='Count')
plt.figure(figsize=(12, 8))
sns.barplot(x='Issue Type', y='Count', hue='Priority', data=priority_df_melted)
plt.title('Priority Levels')
plt.xticks(rotation=45)
plt.savefig('priority_levels.png')
plt.close()

# Resolution Times
plt.figure(figsize=(10, 6))
sns.lineplot(x='Agent ID', y='Average Resolution Time (mins)', data=agent_performance_df, marker='o')
plt.title('Average Resolution Times by Agent')
plt.savefig('resolution_times.png')
plt.close()

# Customer Satisfaction
plt.figure(figsize=(10, 6))
sns.lineplot(x='Month', y='Average Satisfaction Rating', data=customer_satisfaction_df, marker='o')
plt.title('Customer Satisfaction Over Time')
plt.savefig('customer_satisfaction.png')
plt.close()

# Agent Performance
fig, ax1 = plt.subplots(figsize=(12, 8))
color = 'tab:blue'
ax1.set_xlabel('Agent ID')
ax1.set_ylabel('Average Resolution Time (mins)', color=color)
ax1.bar(agent_performance_df['Agent ID'], agent_performance_df['Average Resolution Time (mins)'], color=color, alpha=0.6)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Average Satisfaction Rating', color=color)
ax2.plot(agent_performance_df['Agent ID'], agent_performance_df['Average Satisfaction Rating'], color=color, marker='o')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Agent Performance')
fig.tight_layout()
plt.savefig('agent_performance.png')
plt.close()

# Print URLs
print('issue_distribution.png')
print('priority_levels.png')
print('resolution_times.png')
print('customer_satisfaction.png')
print('agent_performance.png')
