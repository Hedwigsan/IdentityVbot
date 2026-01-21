# Identity Archive 運用管理ガイド

## システム構成

### 本番環境
- **フロントエンド**: Vercel ([https://identity-archive.vercel.app](https://identity-archive.vercel.app))
- **バックエンドAPI**: Xserver VPS 6GB ([https://api.identityarchive.net](https://api.identityarchive.net))
- **データベース**: Supabase (PostgreSQL + 認証)
- **ドメイン**: identityarchive.net (Cloudflare DNS管理)
- **HTTPS**: Cloudflare Tunnel

### VPS詳細
- **プラン**: Xserver VPS 6GB
- **OS**: Ubuntu 24.04 LTS
- **IPアドレス**: 162.43.8.33
- **CPU**: 4コア
- **メモリ**: 6GB
- **ストレージ**: 150GB NVMe SSD

---

## VPS管理

### SSH接続

```bash
ssh root@162.43.8.33
```

**注意**: SSH公開鍵認証を使用しています。秘密鍵は `C:\Users\gooog\.ssh\id_ed25519` に保存されています。

### systemdサービス管理

システムには2つの主要なサービスがあります:

#### 1. FastAPIバックエンド (`identity-archive.service`)

```bash
# サービスの状態確認
sudo systemctl status identity-archive.service

# サービスの起動
sudo systemctl start identity-archive.service

# サービスの停止
sudo systemctl stop identity-archive.service

# サービスの再起動
sudo systemctl restart identity-archive.service

# ログの確認（リアルタイム）
sudo journalctl -u identity-archive.service -f

# ログの確認（最新100行）
sudo journalctl -u identity-archive.service -n 100
```

#### 2. Cloudflare Tunnel (`cloudflare-tunnel.service`)

```bash
# サービスの状態確認
sudo systemctl status cloudflare-tunnel.service

# サービスの起動
sudo systemctl start cloudflare-tunnel.service

# サービスの停止
sudo systemctl stop cloudflare-tunnel.service

# サービスの再起動
sudo systemctl restart cloudflare-tunnel.service

# ログの確認
sudo journalctl -u cloudflare-tunnel.service -f
```

### サービスファイルの場所

- FastAPI: `/etc/systemd/system/identity-archive.service`
- Cloudflare Tunnel: `/etc/systemd/system/cloudflare-tunnel.service`

### 環境変数の変更

環境変数はsystemdサービスファイルに直接記述されています:

```bash
# サービスファイルを編集
sudo nano /etc/systemd/system/identity-archive.service

# 変更後、設定を再読み込み
sudo systemctl daemon-reload

# サービスを再起動
sudo systemctl restart identity-archive.service
```

**重要な環境変数**:
- `SUPABASE_URL`: SupabaseプロジェクトのURL
- `SUPABASE_KEY`: Supabaseのservice_roleキー（秘密情報）
- `FRONTEND_URL`: フロントエンドのURL（https://identity-archive.vercel.app）

---

## アプリケーション管理

### ソースコードの場所

VPS内のディレクトリ:
```
/opt/identity-archive/
├── backend/          # FastAPIアプリケーション
│   ├── app/         # アプリケーションコード
│   ├── templates/   # OCRテンプレート画像
│   └── venv/        # Python仮想環境
└── .git/            # Gitリポジトリ
```

### コードの更新

```bash
# VPSにSSH接続
ssh root@162.43.8.33

# プロジェクトディレクトリに移動
cd /opt/identity-archive

# 最新のコードをpull
git pull origin master

# Python依存パッケージの更新（必要な場合）
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# サービスを再起動
sudo systemctl restart identity-archive.service

# 正常に起動したか確認
sudo systemctl status identity-archive.service
```

### Python依存パッケージの追加

```bash
cd /opt/identity-archive/backend
source venv/bin/activate

# パッケージをインストール
pip install パッケージ名

# requirements.txtを更新
pip freeze > requirements.txt

# 仮想環境を終了
deactivate

# サービスを再起動
sudo systemctl restart identity-archive.service
```

---

## フロントエンド管理（Vercel）

### 環境変数

Vercelダッシュボード → Settings → Environment Variables で管理:

- `VITE_API_URL`: https://api.identityarchive.net
- `VITE_SUPABASE_URL`: SupabaseプロジェクトのURL
- `VITE_SUPABASE_ANON_KEY`: Supabaseのanonキー

### デプロイ

```bash
# ローカルでコードを変更後
git add .
git commit -m "変更内容"
git push origin master

# Vercelが自動的にデプロイを開始
```

### 手動デプロイ

1. [Vercel Dashboard](https://vercel.com/dashboard) にアクセス
2. プロジェクト「identity-archive」を選択
3. Deployments タブ → 最新のデプロイメント → 「...」メニュー → 「Redeploy」

**環境変数を変更した場合**:
- 「Use existing Build Cache」のチェックを外して再デプロイ

---

## データベース管理（Supabase）

### アクセス

[Supabase Dashboard](https://supabase.com/dashboard) → プロジェクト選択

### テーブル構造

#### matchesテーブル
試合の基本情報を保存

#### survivorsテーブル
各試合のサバイバー情報を保存（matchesテーブルと外部キーで紐付け）

### SQLクエリの実行

Supabase Dashboard → SQL Editor でSQLを直接実行できます。

---

## ドメイン・DNS管理

### ドメイン: identityarchive.net

DNS管理はCloudflareで行っています。

### Cloudflareダッシュボード

[Cloudflare Dashboard](https://dash.cloudflare.com/) → identityarchive.net

### DNSレコード

- **A/CNAME レコード**: Cloudflare Tunnelが自動管理
- **api.identityarchive.net**: VPSのバックエンドAPI

### Cloudflare Tunnel管理

VPSで以下のコマンドを使用:

```bash
# Tunnelの情報を確認
cloudflared tunnel info identity-archive

# Tunnel一覧を確認
cloudflared tunnel list

# Tunnel設定ファイルの場所
cat ~/.cloudflared/config.yml
```

---

## トラブルシューティング

### 1. APIが応答しない

```bash
# VPSにSSH接続
ssh root@162.43.8.33

# FastAPIサービスの状態を確認
sudo systemctl status identity-archive.service

# ログを確認
sudo journalctl -u identity-archive.service -n 100

# サービスが停止している場合は起動
sudo systemctl start identity-archive.service
```

### 2. Cloudflare Tunnelが動作しない

```bash
# Cloudflare Tunnelサービスの状態を確認
sudo systemctl status cloudflare-tunnel.service

# ログを確認
sudo journalctl -u cloudflare-tunnel.service -n 100

# サービスを再起動
sudo systemctl restart cloudflare-tunnel.service
```

### 3. HTTPSでアクセスできない

1. Cloudflare Tunnelサービスが起動しているか確認
2. ブラウザで `https://api.identityarchive.net/health` にアクセスして確認
3. DNSの伝播状況を確認（最大48時間かかる場合があります）

### 4. ログインできない

1. Supabase Dashboard → Authentication → URL Configuration を確認
2. リダイレクトURLに `https://identity-archive.vercel.app/auth/callback` が登録されているか確認
3. ブラウザのlocalStorageをクリア（F12 → Application → Local Storage）

### 5. OCRが動作しない

```bash
# VPSのログを確認
sudo journalctl -u identity-archive.service -n 100 | grep -i error

# メモリ使用量を確認
free -h

# ディスク使用量を確認
df -h
```

### 6. 401エラーが頻発する

- ブラウザのlocalStorageから`access_token`を削除
- 再度ログイン
- 自動ログアウト機能が実装されているため、無効なトークンは自動的にクリアされます

---

## セキュリティ

### 秘密情報の管理

以下の情報は絶対に公開しないでください:

- Supabaseの`service_role`キー
- Supabaseの`SUPABASE_KEY`環境変数
- VPSのSSH秘密鍵
- Cloudflare Tunnelのcredentialsファイル

### ファイアウォール設定

VPSのファイアウォールはXserverパケットフィルターで管理:

- ポート22 (SSH): 許可
- ポート80 (HTTP): 許可
- ポート443 (HTTPS): 許可

### SSH接続のセキュリティ

- パスワード認証は無効化
- 公開鍵認証のみ使用
- rootアカウントでの接続（本番環境では専用ユーザーの使用を推奨）

---

## バックアップ

### データベース（Supabase）

Supabase Dashboard → Settings → Database → Backups で自動バックアップが有効になっています。

### VPSのコード

GitHubリポジトリにpushすることでバックアップされます:

```bash
git push origin master
```

### OCRテンプレート画像

`/opt/identity-archive/backend/templates/icons/` に保存されています。

定期的にローカルにコピーしてバックアップすることを推奨:

```bash
scp -r root@162.43.8.33:/opt/identity-archive/backend/templates/icons ./backup/
```

---

## 監視とメンテナンス

### 定期的な確認項目

**毎日**:
- アプリケーションが正常に動作しているか確認
- エラーログの確認

**毎週**:
- ディスク使用量の確認
- メモリ使用量の確認

**毎月**:
- OSのアップデート
- Python依存パッケージのアップデート

### システムアップデート

```bash
# VPSにSSH接続
ssh root@162.43.8.33

# パッケージリストを更新
apt update

# アップグレード可能なパッケージを確認
apt list --upgradable

# パッケージをアップグレード
apt upgrade -y

# 再起動が必要な場合
reboot
```

**注意**: 再起動後、サービスが自動的に起動することを確認してください。

---

## パフォーマンス最適化

### CPU・メモリ使用状況の確認

```bash
# リアルタイム監視
htop

# またはtop
top

# メモリ使用量
free -h

# ディスク使用量
df -h

# ディスクI/O
iostat
```

### ログローテーション

systemdのログが肥大化する場合:

```bash
# ログサイズを確認
sudo journalctl --disk-usage

# 古いログを削除（例: 7日以前）
sudo journalctl --vacuum-time=7d

# またはサイズ指定（例: 500MB以下に）
sudo journalctl --vacuum-size=500M
```

---

## よくある作業

### 環境変数の確認

```bash
# サービスファイルを表示
cat /etc/systemd/system/identity-archive.service
```

### サービスの自動起動設定確認

```bash
# 自動起動が有効か確認
systemctl is-enabled identity-archive.service
systemctl is-enabled cloudflare-tunnel.service

# 自動起動を有効化
sudo systemctl enable identity-archive.service
sudo systemctl enable cloudflare-tunnel.service
```

### Pythonの仮想環境の再作成

```bash
cd /opt/identity-archive/backend

# 既存の仮想環境を削除
rm -rf venv

# 新しい仮想環境を作成
python3 -m venv venv

# 有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r requirements.txt

# 無効化
deactivate

# サービスを再起動
sudo systemctl restart identity-archive.service
```

---

## 緊急時の連絡先・リソース

### ドキュメント

- FastAPI: https://fastapi.tiangolo.com/
- Supabase: https://supabase.com/docs
- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- Vercel: https://vercel.com/docs

### サポート

- Xserver VPS: https://vps.xserver.ne.jp/support/
- Cloudflare: https://dash.cloudflare.com/ (サポートページ)
- Supabase: https://supabase.com/dashboard (サポートチャット)

---

## 改善履歴

### 2026-01-12: セキュリティと安定性の改善

1. **401エラー時の自動ログアウト**
   - [frontend/src/services/api.ts](frontend/src/services/api.ts#L45-L64)
   - 無効なトークンを検出すると自動的にログアウト

2. **トークンの自動リフレッシュ**
   - [frontend/src/hooks/useAuth.ts](frontend/src/hooks/useAuth.ts#L54-L92)
   - 5分ごとにトークンの有効期限をチェック
   - 有効期限の1時間前に自動リフレッシュ

3. **Cloudflare Tunnelのsystemd化**
   - VPS再起動時も自動的に起動
   - 固定URL（https://api.identityarchive.net）での運用

4. **独自ドメインの導入**
   - identityarchive.net
   - Cloudflare DNS管理によるHTTPS化

---

## まとめ

このシステムは以下の構成で本番稼働しています:

- **URL**: https://identity-archive.vercel.app
- **API**: https://api.identityarchive.net
- **VPS**: Xserver VPS 6GB (162.43.8.33)
- **データベース**: Supabase

問題が発生した場合は、このドキュメントのトラブルシューティングセクションを参照してください。
