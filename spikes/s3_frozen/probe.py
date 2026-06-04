import importlib.resources as ir

# Safe access even under frozen (MultiplexedPath): use '/' chaining (avoid multi-arg joinpath)
p = ir.files("pkgdata") / "data" / "hello.txt"
print("FROZEN_READ:", p.read_text().strip())
