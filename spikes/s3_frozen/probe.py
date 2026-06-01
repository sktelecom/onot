import importlib.resources as ir

# frozen(MultiplexedPath)에서도 안전한 접근: '/' 체이닝 사용(다중 인자 joinpath 회피)
p = ir.files("pkgdata") / "data" / "hello.txt"
print("FROZEN_READ:", p.read_text().strip())
