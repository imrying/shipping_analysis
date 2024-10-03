import pulp

I = [0, 1, 2, 3]
S = [1, 2]
docks = ["Mombasa", "Zanzibar", "Victoria", "Salalah"]
prices = [600, 900, 1100, 1200]

R = [1000, 1200, 1800, 2800]  # Reserve requirements
F = [700, 1800, 2200, 2800]  # use for next harbour
D = [2, 6, 6, 7]
fixed_costs = [200000, 100000, 400000, 300000]

b = pulp.LpVariable.dicts("y", I, cat="Binary")

tankCap = 3500
prob = pulp.LpProblem("Minimering_af_forbrug", pulp.LpMinimize)


h = pulp.LpVariable.dicts("h", ((i, s) for i in I for s in S), lowBound=0)
f = pulp.LpVariable.dicts("f", ((i, s) for i in I for s in S), lowBound=0)
l = pulp.LpVariable.dicts("l", ((i, s) for i in I for s in S), lowBound=0)

# obj = pulp.lpSum([prices[i] * l[(i, s)] for i in I for s in S]) + pulp.lpSum([fixed_costs[i] * y[i] for i in I])
obj = pulp.lpSum([prices[i] * l[(i, s)] for i in I for s in S]) + pulp.lpSum(
    [fixed_costs[i] * b[i] for i in I]
)

use_Fi = False

ctsts = []
# opgave_18

F_e = []
# 0, 01 × Di × hi,1 + 0, 01 × Di × hi,2 − 0, 005 × Di × Fi
for i in range(len(F)):
    ekstra_forbrug = (D[i] * 0.01 * h[i, 1]) + (D[i] * 0.01 * h[i, 2]) - (0.005 * F[i])
    F_e_i = F[i] + ekstra_forbrug
    F_e.append(F_e_i)


# opgave 19

for i in I:
    ctsts.append(l[i, 1] + l[i, 2] <= tankCap * 2 * b[i])


for i in I:
    prob += h[i, 1] <= tankCap
    prob += h[i, 2] <= tankCap


# Constraints


# Betingelse 1
# fis ≤ his ∀i ∈ {0, 1, 2, 3}, s ∈ {1, 2} (1
for i in I:
    for s in S:
        ctsts.append(f[i, s] <= h[i, s])


#  betingelse 2
# his = hi−1,s + lis − fi−1,s ∀i ∈ {1, 2, 3}, s ∈ {1, 2} (2)

for i in I:
    for s in S:
        prev_i = (i - 1) % 4
        ctsts.append(h[i, s] == h[prev_i, s] + l[i, s] - f[prev_i, s])

# Betingelse 3
# h0s = h3s + l0s − f3s ∀s ∈ {1, 2} (3)
"""
for s in S:
    ctsts.append(h[0,s]==h[3,s]+l[0,s]-f[3,s])
"""

# hi1 + hi2 ≥ Ri+1 + Fi

# Betingelse 4:
#    prev_i = (i - 1) % len(I)
#: hi1 + hi2 ≥ Ri+1 + F
for i in [0, 1, 2]:
    if use_Fi:
        next_i = i + 1
        ctsts.append(h[i, 1] + h[i, 2] >= R[next_i] + F[i])
    else:
        next_i = i + 1
        ctsts.append(h[i, 1] + h[i, 2] >= R[next_i] + F_e[i])

# Betingelse 5: h_3,1 + h_3,2 = R_0 + F_3
# h31 + h32 = R0 + F3

if use_Fi:
    ctsts.append(h[3, 1] + h[3, 2] == R[0] + F[3])
else:
    ctsts.append(h[3, 1] + h[3, 2] == R[0] + F_e[3])

# Betingelse 6: f_i1 + f_i2 = F_i
for i in I:
    if use_Fi:
        ctsts.append(f[i, 1] + f[i, 2] == F[i])
    else:
        ctsts.append(f[i, 1] + f[i, 2] == F_e[i])

# opgave 13

"""
for i in I:
    for s in S:
        ctsts.append(h[i,s] >= 0)
        ctsts.append(h[i,s] <= tankCap)
"""
# opagve 14

for i in I:
    ctsts.append(h[(i, 1)] == h[(i, 2)])

for i in I:
    ctsts.append(f[(i, 1)] == f[(i, 2)])


# his Mængden af brændstof i tank s ved afgang fra havn i,
# fis Mængden af brændstofforbrug fra tank s p˚a rejsen fra havn i til havn i + 1,
# lis Mængden af brændstof fyldt i tank s ved havn i,
# Fi Mængden af brændstof, som der er behov for, ved en sejlads fra havn i til havn i + 1,
# Ri Mængden af brændstof, som skal være i reserve, ved ankomst til havn i. I havn 0 er det præcist den mængde, som skal være p˚a skibet

# opagve 18

# ekstra forburg = Di *0.01*(hi1 + hi2-Fi/2)
# fi1 + fi2 = Fi + ekstra forburg
# fi1 + fi2 = Fi + Di *0.01*(hi1 + hi2-Fi/2)

# fi1 + fi2 = Fi + 0.01*Di*hi1 + 0.01*Di*hi2 - Fi*0.005*Di

# fi1 + fi2 - 0.01*Di*hi1* - 0.01*Di*hi2  = Fi - Fi*0.005*Di

print(len(ctsts))


for const in ctsts:
    prob += const

prob += obj

prob.solve()

print(len(ctsts))

for const in ctsts:
    print(const)

print("\n")


print("\n")
print(f"Total Cost (model): {pulp.value(prob.objective):,.2f}\n")
print("\n")
print("data:")

print("Maengden af braendstof fyldt i tank s ved havn i, (l_is)")

data = []

for i in I:
    port_name = docks[i]
    tank1 = l[i, 1].varValue
    tank2 = l[i, 2].varValue
    data.append([port_name, f"{tank1:.2f}", f"{tank2:.2f}"])
print("{:<10} {:>10} {:>10}".format("Port", "Tank 1(mt)", "Tank 2(mt)"))
print("-" * 32)
for row in data:
    print("{:<10} {:>10} {:>10}".format(row[0], row[1], row[2]))


print("\n")

print("Maengden af braendstof i tank s ved afgang fra havn i, (h_is) ")

data2 = []

for i in I:
    port_name = docks[i]
    tank1 = h[i, 1].varValue
    tank2 = h[i, 2].varValue
    data2.append([port_name, f"{tank1:.2f}", f"{tank2:.2f}"])

print("{:<10} {:>10} {:>10}".format("Port", "Tank 1(mt)", "Tank 2(mt)"))
print("-" * 32)
for row in data2:
    print("{:<10} {:>10} {:>10}".format(row[0], row[1], row[2]))


print("\n")
print(
    "Maengden af braendstofforbrug fra tank s paa rejsen fra havn i til havn i + 1, (f_is)"
)
data3 = []

for i in I:
    port_name = docks[i]
    tank1 = f[i, 1].varValue
    tank2 = f[i, 2].varValue
    data3.append([port_name, f"{tank1:.2f}", f"{tank2:.2f}"])

print("{:<10} {:>10} {:>10}".format("Port", "Tank 1(mt)", "Tank 2(mt)"))
print("-" * 32)
for row in data3:
    print("{:<10} {:>10} {:>10}".format(row[0], row[1], row[2]))
