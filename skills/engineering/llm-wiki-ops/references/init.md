# 知识库初始化流程

当检测到 `config/wiki-binding.json` 不存在或无效时，进入初始化流程。

## 场景一：用户已有 LLM Wiki 知识库

1. 让用户提供知识库的 wiki 链接（如 `https://<tenant>.feishu.cn/wiki/xxxxx`）或 space_id。
2. 从链接中解析 root_node_token。
3. 调用 `lark-cli wiki +space-get` 获取 space_id。
4. 调用 `lark-cli wiki +node-list` 列出根节点，识别标准目录结构：
   - 原始资料
   - 词条
   - 我的文章（含成稿、草稿子节点）
   - 索引
   - 更新日志
   - AGENTS.md
5. 如果缺少标准节点，询问用户是否需要补建。
6. 确保 `config/` 目录存在，生成 `config/wiki-binding.json`，填入所有节点 token 和 doc_id。
7. 告知用户绑定成功。

## 场景二：用户没有知识库，需要新建

1. 调用 `lark-cli wiki +space-create` 创建新知识空间，名称为「LLM Wiki」。
2. 在根节点下创建标准目录结构：
   - 「原始资料」（docx 节点，用于存放资料卡）
   - 「词条」（docx 节点，用于存放词条文档）
   - 「我的文章」（docx 节点，下设「成稿」和「草稿」两个子节点）
   - 「索引」（docx 文档，内容目录）
   - 「更新日志」（docx 文档，追加式记录）
   - 「AGENTS.md」（file 节点，AI 运维约定）
3. 为每个文档写入初始内容：
   - 索引：写入标题、说明、空的 A-Z 结构
   - 更新日志：写入标题、说明、第一条 init 日志
   - AGENTS.md：写入标准运维约定
4. 确保 `config/` 目录存在，生成 `config/wiki-binding.json`。
5. 告知用户创建成功，提供知识库链接。

## 绑定文件验证

生成绑定文件后，必须验证：
1. space_id 有效（调用 `wiki +space-get` 确认）。
2. 所有 node_token 有效（调用 `wiki +node-list` 确认子节点存在）。
3. 所有 doc_id 有效（调用 `docs +fetch` 确认可读取）。
4. 验证通过后，在绑定文件中写入 `last_updated` 时间戳。

## 标准目录结构

```text
LLM Wiki（知识空间）
├── 原始资料/     # 资料卡：每个源文件一张，保留原文链接
├── 词条/         # 从资料和文章中提取的实体与概念
├── 我的文章/
│   ├── 成稿/     # 已完成的文章
│   └── 草稿/     # 尚未完成的文章
├── 索引          # 所有词条、资料卡、文章的目录（A-Z 排序）
├── 更新日志      # 每次入库/查询/lint 的追加记录
└── AGENTS.md      # 给 AI Agent 的运维约定
```
