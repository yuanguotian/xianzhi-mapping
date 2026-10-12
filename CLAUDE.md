# 县志农业统计表 · 列映射（云端会话工作说明）

这个仓库只做一件事：按 `mapping_spec.md`，给 `batches/` 里的县志统计表做列映射，结果写进 `results/`。
数值不在这里取；映射结果拉回本地后，由本地脚本按映射从原始转录里取数。

## 文件
- `mapping_spec.md`：映射说明书（铁律、变量清单、字段定义、输出格式）。**每个干活的子代理都必须先完整读一遍。**
- `batches/batch_NNNN.json`：每个文件 50 张表（JSON 数组）。
- `results/map_NNNN.jsonl`：对应批次的映射结果，每张表一行，key 原样复制、顺序与输入一致。
- `check_map.py`：校验脚本，`python3 check_map.py batches/batch_NNNN.json results/map_NNNN.jsonl`，打印 OK 才算完成。

## 怎么做
1. 列出 `batches/` 里还没有对应 `results/map_NNNN.jsonl` 的批次（或者只做用户在提示里指定的批次）。
2. **每个批次派一个子代理**（effort 设为 high），同时最多 4 个。给子代理的任务：
   - 完整读 `mapping_spec.md`；
   - 读 `batches/batch_NNNN.json`；
   - 逐张表判断（可以写小脚本辅助看表、生成 JSON，但判断必须逐张做，不能用关键词规则批量套），写 `results/map_NNNN.jsonl`；
   - 临时脚本放在 `/tmp/work_NNNN/`，不要放进仓库；
   - 跑 `python3 check_map.py batches/batch_NNNN.json results/map_NNNN.jsonl`，不是 OK 就改到 OK；
   - 只做映射，不改任何其他文件，不抄写、不换算任何数值；
   - 最后简短回报：完成张数、进面板张数、映射条目数、说明书不够用或互相矛盾的地方（具体举表例）。
3. 所有批次都 OK 后，把每个子代理回报的"说明书不够用的地方"汇总写进 `results/反馈汇总_<日期>.md`。
4. 提交 `results/` 并推送（只提交 `results/`，不要改 `mapping_spec.md`、`batches/`、`check_map.py`）。

## 不要做的事
- 不要修改说明书来"解决"它没覆盖的情况——照说明书的铁律 4（拿不准就不映射，写进存疑）处理，并记进反馈汇总，由本地统一修订。
- 不要合并、加总、换算任何数，不要改原表内容。
