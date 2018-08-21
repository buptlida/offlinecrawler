area = []
subarea = []
counta = 0
counts = 0
with open("area.txt") as file:
  for line in file:
    info = line.strip().split(":")
    area.append((info[0],counta))
    for s in info[1].strip().split(" "):
      subarea.append((s, counts))
      counts += 1
    counta += 1

subways = []
subway = []
counta = 0
counts = 0
with open("subway.txt") as file:
  for line in file:
    info = line.strip().split(":")
    subways.append((info[0],counta))
    for s in info[1].strip().split(" "):
      subway.append((s, counts))
      counts += 1
    counta += 1

out1 = open("areanum.txt", "w")
for s in area:
  out1.write(s[0] + "\t" + str(s[1]) + "\n")
out1.close()

out2 = open("subareanum.txt", "w")
for s in subarea:
  out2.write(s[0] + "\t" + str(s[1]) + "\n")
out2.close()
    
out3 = open("subwaysnum.txt", "w")
for s in subways:
  out3.write(s[0] + "\t" + str(s[1]) + "\n")
out3.close()
  
out4 = open("subwaynum.txt", "w")
for s in subway:
  out4.write(s[0] + "\t" + str(s[1]) + "\n")
out4.close()
