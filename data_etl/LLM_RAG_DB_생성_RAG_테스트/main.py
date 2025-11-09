# main.py
from rag_engine import RAGEngine

def main():
    print("="*50)
    print(" RAG 기반 Steam 게임 추천 시스템")
    print("="*50)
    print("주의: 처음 실행하는 경우, 터미널에서 'python ingest_data.py'를 먼저 실행하여 데이터베이스를 설정해야 합니다.")
    
    engine = RAGEngine()
    
    try:
        while True:
            question = input("\n질문을 입력하세요 (종료하려면 'exit' 입력): ")
            if question.lower() == 'exit':
                print("시스템을 종료합니다.")
                break
            if not question.strip():
                continue
            
            answer = engine.query(question)
            print("\n[답변]\n", answer)
            print("-" * 50)
    
    except (KeyboardInterrupt, EOFError):
        print("\n강제 종료되었습니다.")
    finally:
        engine.close()

if __name__ == "__main__":
    main()