"""studio/SMK2_Stagger.lua: pure ordering/numbering logic (the Fusion dialog shell is UNVERIFIED and skipped without `comp`)."""
import os, sys
from lupa import LuaRuntime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lua = LuaRuntime(unpack_returned_tuples=True); T = lua.table_from
lua.execute("comp = nil")
lua.execute(open(os.path.join(ROOT, "studio/SMK2_Stagger.lua")).read())
passed = failed = 0
def check(n, c):
    global passed, failed
    if c: passed += 1
    else: failed += 1; print("FAIL:", n)
S = lua.eval("SMK2Stagger")
tools = lambda rows: T([T(dict(name=n, x=x, y=y, sel=s)) for n, x, y, s in rows])
names = lambda t: [t[i]["name"] for i in range(1, len(t) + 1)]
rows = [("C", 30, 0, 1), ("A", 10, 5, 2), ("B", 20, 0, 3), ("D", 20, 9, 4)]
check("left to right (ties: top first)", names(S.order(tools(rows), "x")) == ["A", "B", "D", "C"])
check("top to bottom", names(S.order(tools(rows), "y")) == ["C", "B", "A", "D"])
check("selection order", names(S.order(tools(rows), "sel")) == ["C", "A", "B", "D"])
check("order does not change the input", names(tools(rows)) == ["C", "A", "B", "D"])
check("stable for identical keys", names(S.order(tools([("P", 1, 1, 1), ("Q", 1, 1, 2), ("R", 1, 1, 3)]), "x")) == ["P", "Q", "R"])
store = lua.table()
has = lua.eval("function(t) return t.name ~= 'B' end")
setf = lua.eval("function(store) return function(t, v) store[t.name] = v end end")(store)
done, skipped = S.apply(S.order(tools(rows), "x"), 2, 3, has, setf)
check("numbers start + n*step on tools with an Index input, in order", store["A"] == 2 and store["D"] == 5 and store["C"] == 8)
sl = lambda t: [t[i] for i in range(1, len(t) + 1)]
check("tools without Index are skipped and reported, not numbered", store["B"] is None and sl(skipped) == ["B"] and sl(done) == ["A", "D", "C"])
done2, _ = S.apply(S.order(tools(rows), "x"), 0, -1, lua.eval("function() return true end"), setf)
check("negative step", store["A"] == 0 and store["B"] == -1 and store["C"] == -3)
a, b = S.apply(tools([]), 0, 1, has, setf)
check("empty selection", len(a) == 0 and len(b) == 0)
print(f"stagger: {passed} passed, {failed} failed"); sys.exit(1 if failed else 0)
