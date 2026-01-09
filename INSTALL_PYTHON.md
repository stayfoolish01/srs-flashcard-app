# Pythonインストールガイド

このガイドでは、Windows環境でPython 3.13をインストールする手順を説明します。

## 推奨バージョン

| 項目 | バージョン | 理由 |
|------|----------|------|
| **Python** | **3.13** | Django 5.2 LTSと全ライブラリが完全対応 |
| Django | 5.2 LTS | 長期サポート版で安定 |

## インストール手順

### 1. Pythonのダウンロード

以下の直接リンクからダウンロードしてください（推奨）：

**Python 3.13.11 (64-bit) Windows installer:**
https://www.python.org/ftp/python/3.13.11/python-3.13.11-amd64.exe

または、公式サイトから選択：
https://www.python.org/downloads/

### 2. インストーラーの実行

1. ダウンロードした`python-3.xx.x-amd64.exe`を実行

2. **重要**: インストール画面で以下を確認：
   ```
   ☑ Add python.exe to PATH  <- これに必ずチェック！
   ```

3. 「Install Now」をクリック（推奨）
   - または、「Customize installation」で詳細設定

4. インストール完了まで待機（数分）

5. 「Close」をクリック

### 3. インストール確認

コマンドプロンプトまたはPowerShellを開いて以下を実行：

```bash
python --version
```

出力例：
```
Python 3.12.1
```

バージョンが表示されればインストール成功です！

### 4. pipの確認

Pythonのパッケージマネージャー`pip`も確認：

```bash
pip --version
```

出力例：
```
pip 24.0 from C:\Users\...\Python312\lib\site-packages\pip (python 3.12)
```

## トラブルシューティング

### 問題1: 'python' は、内部コマンドまたは外部コマンド...として認識されていません

**原因**: PATHが設定されていない

**解決策**:

#### 方法A: 再インストール（推奨）
1. Pythonをアンインストール
2. 再度インストール時に「Add python.exe to PATH」にチェック

#### 方法B: 手動でPATHを追加
1. Windowsキー + R → `sysdm.cpl` → Enter
2. 「詳細設定」タブ → 「環境変数」
3. 「システム環境変数」の「Path」を選択 → 「編集」
4. 「新規」をクリックして以下を追加：
   ```
   C:\Users\<ユーザー名>\AppData\Local\Programs\Python\Python312\
   C:\Users\<ユーザー名>\AppData\Local\Programs\Python\Python312\Scripts\
   ```
5. すべてのウィンドウでOKをクリック
6. **コマンドプロンプトを再起動**

### 問題2: Microsoft Storeが開く

**原因**: Windows 10/11のPythonエイリアス

**解決策**:
1. Windowsの設定を開く
2. 「アプリ」→「アプリと機能」→「アプリ実行エイリアス」
3. 「アプリインストーラー python.exe」をオフ
4. 「アプリインストーラー python3.exe」をオフ

### 問題3: 複数のPythonバージョンがインストールされている

**確認方法**:
```bash
where python
```

**解決策**:
- 使いたいバージョンのPATHを環境変数の上位に移動
- または、`py -3.12 --version`のようにバージョン指定

## インストール後の次のステップ

Pythonのインストールが完了したら：

### Windows

1. **コマンドプロンプトを開く**
   - Windowsキー → 「cmd」と入力 → Enter

2. **プロジェクトディレクトリに移動**
   ```bash
   cd C:\Users\kayabe\Desktop\ML\AI_project\srs-flashcard-app
   ```

3. **自動セットアップスクリプトを実行**
   ```bash
   setup.bat
   ```

このスクリプトが以下を自動で実行します：
- Python仮想環境の作成
- 依存パッケージのインストール
- .envファイルの作成
- Node.jsパッケージのインストール（Node.jsがある場合）

### macOS/Linux

macOSやLinuxを使用している場合：

```bash
cd srs-flashcard-app

# Python仮想環境作成
python3 -m venv venv

# 仮想環境有効化
source venv/bin/activate

# 依存パッケージインストール
pip install -r requirements.txt

# 環境変数ファイル作成
cp .env.example .env

# Node.jsパッケージインストール
npm install
```

## Node.jsのインストール（オプション）

Tailwind CSSを使用するには、Node.js 18以上が必要です：

**https://nodejs.org/**

- LTS版（推奨）をダウンロード
- インストーラーを実行
- デフォルト設定でOK

確認：
```bash
node --version
npm --version
```

## ヘルプ

問題が解決しない場合：
- [SETUP.md](SETUP.md)の詳細なガイドを確認
- [GitHub Issues](https://github.com/stayfoolish01/srs-flashcard-app/issues)で質問

---

**準備ができたら、`setup.bat`を実行してプロジェクトのセットアップを開始してください！**
