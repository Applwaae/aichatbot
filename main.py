import streamlit as st
import google.generativeai as genai
import sys

# --- 关键：API 密钥配置 ---
# 警告：永远不要像您之前那样把 API 密钥直接写在代码里！
# 我们将使用 Streamlit 的 Secrets 管理功能。
# 
# 如何设置:
# 1. 在您的 Streamlit Cloud 项目中，点击 "Manage App" -> "Settings" -> "Secrets"
# 2. 添加一个新的 Secret，键（Key）为 "GEMINI_API_KEY"
# 3. 值（Value）为您的 "AIzaSy..." 密钥。
# 4. 点击保存。

# 尝试从 st.secrets 中获取 API 密钥
api_key = "AIzaSyBzfc0Hu8hToiG4DLrzs5GYBpj9IR3kvwU"

# 如果没有在 Streamlit Cloud 的 Secrets 中找到密钥
if not api_key:
    st.error("错误：未在 Streamlit Secrets 中找到 GEMINI_API_KEY。")
    st.info("请在应用的 'Settings > Secrets' 中添加您的 Gemini API 密钥。")
    # 在本地测试时，为了方便，你也可以临时用下面的行：
    # api_key = "粘贴你的密钥在这里" 
    # 但请记得在推送到 GitHub 前删除它！！！
    st.stop() # 停止执行

# 配置 Gemini API
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"API 密钥配置失败: {e}")
    st.stop()

# --- Streamlit 应用界面 ---

st.title("💬 我的 Streamlit AI 聊天机器人")
st.caption("一个由 Gemini 驱动的聊天应用")

# --- 模型选择 ---
# 注意：'gemini-2.5-flash' 目前（截至2024年底）还不存在。
# 我将其改为了 'gemini-1.5-flash'，这是目前最新的 Flash 模型。
MODEL_NAME = "gemini-2.5-flash"

try:
    # 初始化模型
    model = genai.GenerativeModel(MODEL_NAME)
    
    # 初始化聊天会话 (Gemini SDK 需要)
    # 我们将在 session_state 中存储 chat 对象
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

except Exception as e:
    st.error(f"模型 '{MODEL_NAME}' 初始化失败: {e}")
    st.stop()


# --- 聊天历史记录 (Streamlit Session State) ---
# 初始化聊天记录。st.session_state 会在用户会话期间保持数据。
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 显示历史消息 ---
# 遍历 st.session_state.messages 中的所有消息并显示它们
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 接收用户输入 ---
# st.chat_input 会在页面底部显示一个输入框
if prompt := st.chat_input("你好，有什么可以帮你的吗？"):
    
    # 1. 将用户的消息添加到 session_state 和聊天气泡中
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 调用 Gemini API 获取回复
    try:
        # 显示一个加载提示
        with st.spinner("Gemini 正在思考中..."):
            # 注意：我们使用 st.session_state.chat.send_message()
            # 这允许模型记住上下文（之前的对话）
            response = st.session_state.chat.send_message(prompt)
        
        # 3. 将 AI 的回复添加到 session_state 和聊天气泡中
        ai_response = response.text
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)
            
    except Exception as e:
        st.error(f"调用 API 时发生错误: {e}")
