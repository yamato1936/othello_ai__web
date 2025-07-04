# オセロAI Webアプリケーション

## 概要
モンテカルロ木探索（MCTS）アルゴリズムを搭載した、Webブラウザで遊べるオセロAIアプリケーションです。

このプロジェクトは、単にオセロAIを実装するだけでなく、Webアプリケーションとして公開する上で直面するパフォーマンス問題に対し、Celeryを用いた非同期処理やDockerによるコンテナ化といった、モダンな技術を用いて解決することに挑戦しました。

デモアプリはこちらからプレイできます！
https://othello-web-iiy2.onrender.com/


## 主な機能
AIとの対戦: 序盤・中盤・終盤で思考を切り替える、動的評価関数を搭載したMCTS AIと対戦できます。

非同期AI: AIの思考中もUIが固まることなく、快適にプレイできます。

合法手表示: プレイヤーが石を置ける場所をハイライト表示します。

セッション管理: 複数人が同時にアクセスしても、それぞれのゲームが独立して進行します。

## 技術スタック
バックエンド: Python, Flask

非同期タスクキュー: Celery, Redis

フロントエンド: HTML, CSS, JavaScript

AIアルゴリズム: モンテカルロ木探索 (MCTS) with 動的評価関数

インフラ・デプロイ: Docker, Gunicorn, Render

## AIのロジックについて
このアプリに搭載されているAIは、モンテカルロ木探索（MCTS） というアルゴリズムに基づいています。MCTSは、以下の4つのステップを繰り返すことで、最も勝率の高い手を見つけ出します。

### 選択 (Selection): 
現在の局面から、最も有望そうな手（UCTスコアが高い手）をたどって、末端のノードまで進みます。

### 展開 (Expansion): 
まだ試していない手の中から一つを選び、新しいノードとして木に追加します。

### シミュレーション (Simulation): 
新しく追加したノードから、ゲーム終了までランダムに手を打ち続け、勝敗をシミュレートします。

【高速化の工夫】: このアプリでは、シミュレーションを最後まで行う代わりに、一定の手数だけ進めた後の盤面を、**序盤・中盤・終盤で重み付けを変える動的評価関数（teacher_ai.py）**で評価しています。これにより、計算時間を大幅に短縮しつつ、精度の高い評価を可能にしています。

### 更新 (Backpropagation):
シミュレーションの結果（勝ち/負け）を、末端のノードからルートノードまでフィードバックし、各ノードの勝率データを更新します。

このサイクルを何百回（iterationsの数だけ）も繰り返すことで、AIは統計的に最も勝つ確率が高い「最善の一手」を導き出します。

また、Dockerfile内で起動用のシェルスクリプト (start.sh) を作成しました。このスクリプトは、1つのWebサービスコンテナが起動する際に、以下の2つのプロセスを同時に起動します。



```
ファイル構成
/othello_ai_web
|
|-- app.py             # Flaskメインアプリ。API定義とセッション管理
|-- tasks.py           # Celeryのタスク定義。AI思考の非同期処理
|-- othello_ai.py      # オセロのルールや盤面を管理するクラス
|-- mcts_ai.py         # MCTSアルゴリズムの実装
|-- teacher_ai.py      # MCTSが使用する動的評価関数
|-- requirements.txt   # 必要なPythonライブラリ
|-- Dockerfile         # アプリケーションをコンテナ化するための設計図
|-- render.yaml        # Renderでインフラをコードとして定義するための設計図
|-- .gitignore         # Gitの追跡から除外するファイルを設定
|
|-- templates/
|   |-- index.html     # ゲーム画面のHTML
|
|-- static/
    |-- css/
    |   |-- style.css  # デザイン用のCSS
    |-- js/
        |-- main.js    # ゲームの動きを制御するJS

```

## ローカルでの実行方法
リポジトリをクローンします。

```
git clone [https://github.com/yamato1936/othello_ai__web.git](https://github.com/yamato1936/othello_ai__web.git)
cd othello_ai__web
```
必要なライブラリをインストールします。

```
pip install -r requirements.txt
```

Dockerを使ってRedisサーバーを起動します。

```
docker run -d -p 6379:6379 redis
```

別のターミナルでCeleryワーカーを起動します。

```
celery -A tasks.celery worker --loglevel=info
```

さらに別のターミナルでFlaskアプリを起動します。

```
flask run
```

ブラウザで http://127.0.0.1:5000 にアクセスします。
