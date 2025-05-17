import ast
import matplotlib.pyplot as plt

# Load the data from the .txt file as a dictionary
with open("../../docs/stats/Issue_Distribution_in_414_Events.txt", "r") as f:            # other one with 2029 events
    issue_event_counts = ast.literal_eval(f.read())

print(issue_event_counts)

# Sort by count descending
# sorted_issues = sorted(issue_event_counts.items(), key=lambda x: x[1], reverse=True)
sorted_issues = sorted(issue_event_counts.items(), key=lambda x: x[1], reverse=True)[:20]   # just get TOP 50
issues, counts = zip(*sorted_issues)

# Plot horizontal bar chart
plt.figure(figsize=(12, 18))
plt.barh(issues, counts)
plt.xlabel("Number of Events")
# Add x-axis gridlines
plt.grid(axis='x', linestyle='--', alpha=0.6)
# plt.title("Event Distribution Across Political Issues (900 articles)")          # (Full Corpus)
plt.title("Top 20 Issues Represented in 414 Curated Events (900 Articles)")
plt.gca().invert_yaxis()
plt.tight_layout()

# Save and show chart
output_path = "../results_figures/event_distribution_chart.png"
plt.savefig(output_path)
plt.show()
