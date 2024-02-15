## GEMINI-PRO-BOT

**由 Google 的 `gemini-pro` LLM API 驱动的 Python Telegram 机器人**

*这是一个 Python Telegram 机器人，它使用 Google 的 gemini-pro LLM API 根据用户输入生成创意文本格式。它旨在成为一种有趣且互动的方式来探索大型语言模型的可能性。*

[Gemini 机器人预览](https://github.com/rabilrbl/gemini-pro-bot/assets/63334479/ffddcdfa-09c2-4f02-b14d-4407e888b605)

### 特性

- 生成创意文本格式，如诗歌、代码、脚本、音乐作品等。
- 流式处理生成过程，以便你可以实时查看文本展开。
- 用 Bard 的创意输出回复你的消息。
- 使用简单的命令易于使用：
  - `/start`：向机器人问好并开始。
  - `/help`：获取有关机器人功能的信息。
- 发送任何文本消息以触发生成过程。
- 发送带有标题的任何图像以根据图像生成响应。（多模态支持）
- 用户身份验证以通过在 `.env` 文件中设置 `AUTHORIZED_USERS` 来防止未经授权的访问（可选）。

### 分支特性

- 中文化
- 将身份验证由用户名+用户ID验证调整为群组ID+用户ID的方式

### 要求

- Python 3.10+
- Telegram 机器人 API 令牌
- Google `gemini-pro` API 密钥
- dotenv（用于环境变量）

### Docker

#### GitHub 容器镜像仓库

只需运行以下命令即可从 GitHub Container Registry 运行预构建的x86镜像：

```shell
docker run --env-file .env ghcr.io/juewuy/gemini-pro-bot:latest
```

升级:

```shell
docker pull ghcr.io/juewuy/gemini-pro-bot:latest
```

#### 构建

```
git clone https://github.com/juewuy/gemini-pro-bot.git
cd gemini-pro-bot
```

使用以下命令构建映像：

```shell
docker build -t gemini-pro-bot .
```

之后创建一个

```
.env
```

文件并添加以下环境变量：

- `BOT_TOKEN`：你的 Telegram 机器人 API 令牌。你可以通过与 [@BotFather](https://t.me/BotFather) 交谈来获取一个。
- `GOOGLE_API_KEY`：你的 Google Bard API 密钥。你可以从 [Google AI Studio](https://makersuite.google.com/) 获取一个。
- `AUTHORIZED_USERS`：一个以逗号分隔的 Telegram用户ID或者群组ID列表，这些用户/群组将被授权访问机器人。（可选）示例值：`-1234567890123,-1234567890125,1234567890`

最终，使用以下命令运行：

```shell
docker run --env-file .env gemini-pro-bot
```

### Python

1. 克隆此存储库。

   ```shell
   git clone https://github.com/juewuy/gemini-pro-bot.git
   cd gemini-pro-bot
   ```

2. 安装所需的依赖项：

   - `pipenv install`（如果使用 pipenv）
   - `pip install -r requirements.txt`（如果不使用 pipenv）

3. 创建一个

   ```
   .env
   ```

   文件并添加以下环境变量：

   - `BOT_TOKEN`：你的 Telegram 机器人 API 令牌。你可以通过与 [@BotFather](https://t.me/BotFather) 交谈来获取一个。
   - `GOOGLE_API_KEY`：你的 Google Bard API 密钥。你可以从 [Google AI Studio](https://makersuite.google.com/) 获取一个。
   - `AUTHORIZED_USERS`：一个以逗号分隔的 Telegram用户ID或者群组ID列表，这些用户/群组将被授权访问机器人。（可选）示例值：`-1234567890123,-1234567890125,1234567890`

4. 运行机器人：

   - `python main.py`（如果不使用 pipenv）
   - `pipenv run python main.py`（如果使用 pipenv）

### 用法

1. 通过运行脚本启动机器人。

   ```shell
   python main.py
   ```

2. 在你的 Telegram 聊天中打开机器人。

3. 向机器人发送任何文本消息。

4. 机器人将根据你的输入生成创意文本格式，并将结果流式传输回你。

5. 如果你希望限制公众对机器人的访问，你可以在 `.env` 文件中将 `AUTHORIZED_USERS` 设置为 Telegram 用户 ID 或者群组ID的逗号分隔列表。只有这些用户才能访问机器人。
   示例：

   ```shell
   AUTHORIZED_USERS=-1234567890123,-1234567890125,1234567890
   ```

### 机器人命令

| 命令     | 描述                       |
| -------- | -------------------------- |
| `/start` | 向机器人问好并开始。       |
| `/help`  | 获取有关机器人功能的信息。 |
| `/new`   | 开始一个新的聊天会话。     |

### License

This is a free and open-source project released under the GNU Affero General Public License v3.0 license. See the LICENSE file for details.
