# agent.py
from . import config
from .steam_tools import SteamToolbelt

class SteamGameAgent:
    """
    사용자의 질문에 포함된 키워드를 기반으로 적절한 도구를 호출하는 에이전트입니다.
    """
    def __init__(self):
        self.tools = SteamToolbelt()
        print("키워드 기반 SteamGameAgent가 초기화되었습니다.")

    def route_query(self, query: str) -> tuple[str, str]:
        """
        사용자 쿼리에 '계산' 또는 '설명' 키워드가 있는지 확인하여
        Text-to-SQL 또는 RAG 도구를 직접 실행합니다.
        """
        query_lower = query.lower()

        # --- [핵심 수정] LLM 라우팅을 명시적인 키워드 분기로 변경 ---
        try:
            if '계산' in query_lower:
                print("-> '계산' 키워드 감지. 'structured' 도구 (Text-to-SQL)를 실행합니다.")
                tool_name = "structured (Text-to-SQL)"
                # "계산" 키워드 자체는 LLM에게 불필요하므로 제거 후 전달
                clean_query = query.replace('계산', '').strip()
                result = self.tools.query_structured_data(clean_query)
                return result, tool_name

            elif '설명' in query_lower:
                print("-> '설명' 키워드 감지. 'unstructured' 도구 (RAG)를 실행합니다.")
                tool_name = "unstructured (RAG)"
                # "설명" 키워드 자체는 LLM에게 불필요하므로 제거 후 전달
                clean_query = query.replace('설명', '').strip()
                result = self.tools.query_unstructured_data(clean_query)
                return result, tool_name
            
            else:
                # 지정된 키워드가 없는 경우, 사용자에게 사용법 안내
                tool_name = "No Tool Used"
                guide_message = (
                    "Steam 게임 정보가 필요하신가요?\n"
                    "정확한 수치나 계산이 필요하시면 질문에 '계산'을,\n"
                    "게임 추천이나 정보가 필요하시면 '설명'을 포함하여 질문해주세요.\n\n"
                    "예시:\n"
                    "  - 스팀에서 가장 비싼 게임 계산\n"
                    "  - 스팀에서 FromSoftware가 만든 게임 설명"
                )
                return guide_message, tool_name

        except Exception as e:
            error_message = f"에이전트 처리 중 오류 발생: {e}"
            return error_message, "Error"

    def close_connections(self):
        """Toolbelt의 DB 연결을 종료합니다."""
        self.tools.close()

