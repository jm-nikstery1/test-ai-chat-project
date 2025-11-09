# main.py
from . import config
import google.generativeai as genai
from .agent import SteamGameAgent
from datetime import datetime

def save_conversation_log(history: list, filename_base: str):
    """Saves the conversation history to .md and .txt files."""
    md_filename = f"{filename_base}.md"
    txt_filename = f"{filename_base}.txt"
    
    print(f"\n대화 기록을 {md_filename} 및 {txt_filename} 파일로 저장합니다...")

    try:
        # Save Markdown file
        with open(md_filename, 'w', encoding='utf-8') as f_md:
            f_md.write(f"# Steam 챗봇 대화 기록 ({filename_base})\n\n")
            for turn in history:
                f_md.write(f"** 당신:**\n{turn['user']}\n\n")
                if turn['tool']:
                    f_md.write(f"> _[사용한 도구: {turn['tool']}]_\n\n")
                f_md.write(f"** {turn['speaker']}:**\n```text\n{turn['bot']}\n```\n\n---\n\n")
        
        # Save TXT file
        with open(txt_filename, 'w', encoding='utf-8') as f_txt:
            f_txt.write(f"Steam 챗봇 대화 기록 ({filename_base})\n\n")
            for turn in history:
                f_txt.write(f" 당신:\n{turn['user']}\n\n")
                if turn['tool']:
                    f_txt.write(f"[사용한 도구: {turn['tool']}]\n\n")
                f_txt.write(f" {turn['speaker']}:\n{turn['bot']}\n\n")
                f_txt.write("="*60 + "\n\n")
        
        print("파일 저장이 완료되었습니다.")
    
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")


def main():
    """Runs the main conversation loop and saves the log on exit."""
    print("="*60)
    print("Steam 게임 챗봇 어시스턴트 (일반 대화도 가능)")
    print("게임에 대해 질문하시려면 '스팀' 또는 'steam'을 포함하여 질문해주세요.")
    print("종료하시려면 'exit' 또는 '종료'를 입력하세요.")
    print("="*60)

    # List to store conversation history
    conversation_history = []
    
    # Initialize Gemini model for general chat
    genai.configure(api_key=config.GOOGLE_API_KEY)
    general_chat_model = genai.GenerativeModel(config.GEMINI_MODEL_NAME)
    chat = general_chat_model.start_chat(history=[])

    # Initialize the specialized Steam Game Agent
    steam_agent = SteamGameAgent()

    try:
        while True:
            user_input = input("\n당신: ")
            if user_input.lower() in ['exit', '종료']:
                print("프로그램을 종료합니다.")
                break
            
            if not user_input.strip():
                continue

            # Detect keyword to activate the agent
            if "스팀" in user_input or "steam" in user_input.lower():
                response, tool_name = steam_agent.route_query(user_input)
                speaker = "게임 어시스턴트"
                print(f"\n[{speaker}]:\n{response}")
                # Append to conversation history
                conversation_history.append({
                    "user": user_input, 
                    "bot": response, 
                    "tool": tool_name,
                    "speaker": speaker
                })
            else:
                # General conversation
                response = chat.send_message(user_input)
                bot_response_text = response.text
                speaker = "Gemini"
                print(f"\n[{speaker}]:\n{bot_response_text}")
                # Append to conversation history
                conversation_history.append({
                    "user": user_input,
                    "bot": bot_response_text,
                    "tool": "General Chat", # Mark the tool as General Chat
                    "speaker": speaker
                })

    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 강제 종료합니다.")
    finally:
        # Safely close DB connections on exit
        steam_agent.close_connections()
        # Save conversation log to files if it exists
        if conversation_history:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"conversation_log_{timestamp}"
            save_conversation_log(conversation_history, filename_base)

if __name__ == "__main__":
    main()

