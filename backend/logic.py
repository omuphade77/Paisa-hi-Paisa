from typing import List, Dict, Any, Tuple

def validate_and_extract_chains(jobs: List[str], dependencies: Dict[str, List[str]]) -> List[List[str]]:
    parents = {j: [] for j in jobs}
    children = {j: [] for j in jobs}

    for j, deps in dependencies.items():
        for d in deps:
            parents[j].append(d)
            children[d].append(j)

    for j in jobs:
        if len(parents[j]) > 1:
            raise ValueError(f"Job {j} has multiple dependencies — not a linear chain.")
        if len(children[j]) > 1:
            raise ValueError(f"Job {j} has multiple dependents — branching not allowed.")

    indegree = {j: len(parents[j]) for j in jobs}
    visited = set()
    chains = []

    for job in jobs:
        if indegree[job] == 0:
            chain = []
            cur = job
            while cur and cur not in visited:
                chain.append(cur)
                visited.add(cur)
                cur = children[cur][0] if children[cur] else None
            chains.append(chain)

    if len(visited) != len(jobs):
        raise ValueError("Graph contains cycles or disconnected nodes.")

    return chains


def build_prefixes(chains: List[List[str]], job_info: Dict[str, Dict[str, Any]]) -> List[List[Tuple[int, int, List[str]]]]:
    prefixes = []
    for chain in chains:
        pref = [(0, 0, [])]
        t_sum, p_sum = 0, 0
        jobs_acc = []
        for node in chain:
            t_sum += job_info[node]["runtime"]
            p_sum += job_info[node]["profit"]
            jobs_acc.append(node)
            pref.append((int(t_sum), int(p_sum), jobs_acc.copy()))
        prefixes.append(pref)
    return prefixes


def knapsack(prefixes: List[List[Tuple[int, int, List[str]]]], capacity: int):
    n = len(prefixes)
    dp = [0] * (capacity + 1)
    choice = [[0] * (capacity + 1) for _ in range(n)]

    for i in range(n):
        new_dp = dp[:]
        for w in range(capacity + 1):
            for k, (t, p, jobs) in enumerate(prefixes[i]):
                if t <= w and dp[w - t] + p > new_dp[w]:
                    new_dp[w] = dp[w - t] + p
                    choice[i][w] = k
        dp = new_dp

    max_profit = max(dp)
    used_time = dp.index(max_profit)

    # reconstruction
    w = used_time
    selected_prefixes = []
    for i in range(n - 1, -1, -1):
        k = choice[i][w]
        t, p, jobs = prefixes[i][k]
        selected_prefixes.append(jobs)
        w -= t
    selected_prefixes.reverse()
    sequence = [job for prefix in selected_prefixes for job in prefix]

    return max_profit, used_time, sequence
