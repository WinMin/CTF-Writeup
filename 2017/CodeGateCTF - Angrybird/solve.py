import angr

main = 0x4007DA
find = 0x404FBC
avoid = [0x400590]

p = angr.Project('./angrybird2')
init = p.factory.blank_state(addr=main)
pg = p.factory.path_group(init, threads=8)
ex = pg.explore(find=find, avoid=avoid)

final = ex.found[0].state
flag = final.posix.dumps(0)

print("Flag: {0}".format(final.posix.dumps(1)))