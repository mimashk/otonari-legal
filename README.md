# otonari-legal

妊活・不妊治療のお薬アラーム **Otonari** の法務文書とサポートページ。
GitHub Pages で公開している。

| | |
|---|---|
| プライバシーポリシー | `privacy-policy.html` |
| 利用規約 | `terms-of-service.html` |
| サポート | `support.html` |

---

## ⚠️ このリポジトリに Markdown の原本は無い

**原本はアプリのリポジトリ（非公開）にある。**

```
../fertility-med-reminder/docs/legal/*.md   ← 原本。ここを直す
./*.html                                    ← 生成物。直接編集しない
```

★**2つのリポジトリを同じ階層に置く前提**。コピーを持たないのは、
二重管理になると実装を変えたときに片方だけ直るため。

## 更新のしかた

```bash
# ① 原本を直す（アプリのリポジトリ側）
#    fertility-med-reminder/docs/legal/privacy-policy.md など

# ② ここで変換する
python3 build.py

# ③ 生成された HTML をコミットして push
git add -A && git commit -m "法務文書を更新" && git push
```

⚠️ **HTML を直接編集しないこと。** 次の `build.py` で上書きされる。

## 公開設定

GitHub の Settings → Pages → Source を **Deploy from a branch** にし、
`main` / `/ (root)` を選ぶ。

★`.nojekyll` を置いてあるので Jekyll は走らない。HTML をそのまま配信する。

## URL を入れる場所

公開したら、**3か所**に入れる。

1. App Store Connect（プライバシーポリシーURL / **サポートURL**）
2. Play Console（プライバシーポリシーURL）
3. RevenueCat のペイウォール（利用規約・プライバシーポリシーのリンク）

⚠️ 3 が空のままだと Apple のガイドライン 3.1.2 で弾かれる。
