---
name: push-github
description: Commit and push the whole project to the GitHub repo zhangxichun2026/zxc via SSH. 当用户说 提交github、提交到github、push整个项目到github、推送到zxc仓库 时使用。Do not use for pushing to the Gitee origin or for plain local commits without push.
---

# 提交 GitHub

把当前项目（D:\高级网页vscode）的全部变更提交并推送到 GitHub 仓库 `zhangxichun2026/zxc`（SSH 公钥已配置）。

## 步骤

1. `git status` 查看变更；`git log --oneline -3` 了解提交信息风格（中文一句话，如「添加 14-1.html」）。
2. 用户要求推送整个项目，暂存全部变更：`git add -A`。
3. 提交：`git commit -m "简明中文描述"`。
4. 确认远程：`git remote -v`。若名为 `github` 的远程不存在，执行 `git remote add github git@github.com:zhangxichun2026/zxc.git`（SSH 公钥已配置，用 SSH 地址）。
5. 推送：`git push github master`；首次推送用 `git push -u github master` 建立跟踪。
6. 校验：推送输出应包含 `master -> master`；然后可 `git log --oneline -1` 确认提交。

## 注意

- 环境是 Windows PowerShell 5：不支持 `&&`（用单独命令或 `;` 分隔）；不要用 heredoc 拼提交信息，直接用 `-m`。
- `origin` 是 Gitee 远程，本技能只操作 `github` 远程，不要动 `origin`。
- 推送被拒（远程已有无关历史）时停下来询问用户，禁止 `--force`。
- 含密钥或凭据的文件不得提交。
