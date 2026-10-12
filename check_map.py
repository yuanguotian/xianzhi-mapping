"""
映射结果校验（只用标准库，云端会话里直接跑）
用法: python3 check_map.py batches/batch_0001.json results/map_0001.jsonl
检查：每行合法 JSON；行数=输入张数；key 集合与顺序一致；字段齐全；结构/地域取值合法；
      变量名在 mapping_spec.md 变量清单里；列号在表头范围内；行号在完整表行数范围内；跳过行/年份行在范围内。
全部通过打印 OK 并返回 0；否则逐条列出问题并返回 1。
"""
import re
import sys
import json
from pathlib import Path

HERE = Path(__file__).parent
SPEC = (HERE / 'mapping_spec.md').read_text(encoding='utf-8')
VARS = set(re.findall(r'^\| [^|]+ \| ([^|]+?) \|', SPEC.split('## 变量清单')[1].split('## 表级字段')[0], re.M)) - {'变量', '---'}
STRUCTS = {'行=年份', '列=年份', '行=年份×指标', '单年分地区', '单年分项', '其他'}
AREAS = {'全县', '部分', '上级', '不明'}
TABLE_KEYS = ['key', '地域', '地域名', '结构', '年份', '合计行', '跳过行', '纪年', '年份行', '进面板', '不进理由', '映射', '存疑', '备注']
ENTRY_KEYS = ['列', '行', '行筛选', '子项按行', '年份', '格内位置', '变量', '子项', '单位', '单位来源', '口径', '口径列', '分段口径', '时点', '存疑']


def main(batch, result):
    tabs = json.loads(Path(batch).read_text(encoding='utf-8'))
    errs, maps = [], []
    for i, line in enumerate(Path(result).read_text(encoding='utf-8').splitlines()):
        if not line.strip():
            continue
        try:
            maps.append(json.loads(line))
        except json.JSONDecodeError as e:
            errs.append(f'第 {i + 1} 行不是合法 JSON: {e}')
    if len(maps) != len(tabs):
        errs.append(f'行数 {len(maps)} ≠ 输入张数 {len(tabs)}')
    for i, (t, m) in enumerate(zip(tabs, maps)):
        tag = f'#{i} {str(t.get("表名"))[:20]}'
        if m.get('key') != t['key']:
            errs.append(f'{tag}: key 不一致或顺序不对')
        for k in TABLE_KEYS:
            if k not in m:
                errs.append(f'{tag}: 缺表级字段 {k}')
        if m.get('结构') not in STRUCTS:
            errs.append(f'{tag}: 结构非法 {m.get("结构")!r}')
        if m.get('地域') not in AREAS:
            errs.append(f'{tag}: 地域非法 {m.get("地域")!r}')
        ncol = len(t.get('表头') or [])
        nrow = t.get('总行数') or len(t.get('数据行') or [])
        for r in (m.get('跳过行') or []) + (m.get('年份行') or []):
            if not (isinstance(r, int) and 0 <= r < nrow):
                errs.append(f'{tag}: 跳过行/年份行 {r} 越界（共 {nrow} 行）')
        if m.get('进面板') and (m.get('地域') != '全县' or not m.get('映射')):
            errs.append(f'{tag}: 进面板=true 但地域不是全县或没有映射')
        for e in m.get('映射') or []:
            for k in ENTRY_KEYS:
                if k not in e:
                    errs.append(f'{tag}: 条目缺字段 {k}')
            if e.get('变量') not in VARS:
                errs.append(f'{tag}: 变量不在清单 {e.get("变量")!r}')
            j, r = e.get('列'), e.get('行')
            if j is not None and not (isinstance(j, int) and 0 <= j < ncol):
                errs.append(f'{tag}: 列号 {j} 越界（共 {ncol} 列）')
            if r is not None and not (isinstance(r, int) and 0 <= r < nrow):
                errs.append(f'{tag}: 行号 {r} 越界（共 {nrow} 行）')
            if j is None and r is None:
                errs.append(f'{tag}: 条目既没有列也没有行')
    if errs:
        print('\n'.join(errs))
        return 1
    print(f'OK {len(maps)} 张')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
