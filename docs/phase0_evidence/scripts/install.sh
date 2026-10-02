#!/bin/bash
# Installs dist fuses into Resolve with a print() tee to results/console.log (harness-only instrumentation)
cd /d/SMK/SMKV2/smk-v2
DST="$APPDATA/Blackmagic Design/DaVinci Resolve/Support/Fusion/Fuses"
cat > /tmp/hdr.lua <<'H'
do local _p=print; local LOGF="D:/SMK/SMKV2/smk-v2/results/console.log"
print=function(...) _p(...); local t={} for i=1,select("#",...) do t[#t+1]=tostring((select(i,...))) end
local f=io.open(LOGF,"a"); if f then f:write(os.date("%H:%M:%S ")..table.concat(t," \t"),"\n"); f:close() end end end
H
for f in dist/spikes/*.fuse dist/fuses/*.fuse; do { cat /tmp/hdr.lua; cat "$f"; } > "$DST/$(basename $f)"; done
