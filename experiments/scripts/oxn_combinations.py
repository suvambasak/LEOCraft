TOTAL_SAT = 30*30
MIN_SAT_PER_ORBIT = 10

os = []
for orbital_plane in range(MIN_SAT_PER_ORBIT, TOTAL_SAT):
    if TOTAL_SAT % orbital_plane == 0 and TOTAL_SAT/orbital_plane >= MIN_SAT_PER_ORBIT:
        print((orbital_plane, int(TOTAL_SAT/orbital_plane)))
        os.append(orbital_plane)


print()
print()
print(os)
