#!/usr/bin/env python3
"""
MCP 메모리 클라이언트 - 올바른 구현
LangGraph ReAct Agent와 MCP 서버 연결
"""

import json
import base64
import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('env', override=True)

class MCPMemoryAgent:
    """MCP 메모리 에이전트"""
    
    def __init__(self):
        """클라이언트 초기화"""
        self.client = None
        self.tools = None
        self.llm = None
        self.agent = None
        
    async def initialize(self):
        """비동기 초기화"""
        # OpenAI API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. env 파일을 확인해주세요.")
        
        # ChatOpenAI 초기화
        self.llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.1)
        
        # MCP 클라이언트 설정
        self.client = MultiServerMCPClient({
            "memory": {
                "url": "http://localhost:8084/mcp",
                "transport": "streamable_http"
            }
        })
        
        # 도구 로드
        self.tools = await self.client.get_tools()
        
        # 리소스 로드
        try:
            resources = await self.client.get_resources('memory')
            if resources:
                memory_status = resources[0].as_string()
                print(f"📊 메모리 상태:\n{memory_status}")
        except Exception as e:
            print(f"⚠️ 리소스 로드 중 오류: {e}")
        
        # ReAct 에이전트 생성
        system_prompt = """
당신은 지능적인 AI 어시스턴트입니다. 지식 그래프 기반의 메모리 시스템을 활용하여 사용자와의 대화를 기억하고 관리할 수 있습니다.

### 메모리 관리 원칙:
1. **사용자 식별**: 사용자의 기본 정보(이름, 나이, 직업, 위치 등)를 파악하고 저장합니다.
2. **관계 추적**: 사람들 간의 관계, 조직과의 연결 등을 기록합니다.
3. **행동과 선호도**: 사용자의 관심사, 습관, 선호도를 관찰하고 저장합니다.
4. **목표와 계획**: 사용자의 목표, 계획, 의도를 기억합니다.

### 메모리 활용 방법:
- 대화 시작 시 기존 메모리를 검색하여 사용자 정보를 확인
- 새로운 정보 발견 시 적절한 엔티티와 관계로 저장
- 기존 정보와 연결하여 맥락 유지
- 대화가 끝나면 새롭게 알게 된 중요한 부분을 메모리에 저장

### 사용 가능한 도구들:
- create_entities: 새로운 사람, 조직, 개념 등을 생성
- create_relations: 엔티티 간의 관계 설정
- add_observations: 엔티티에 대한 새로운 정보 추가
- search_nodes: 특정 정보 검색
- read_graph: 전체 메모리 구조 확인

항상 친근하고 도움이 되는 톤으로 대화하며, 사용자의 개인정보를 안전하게 보호합니다.
"""
        
        self.agent = create_react_agent(self.llm, self.tools, prompt=system_prompt)
        
        print("🧠 MCP 메모리 에이전트가 성공적으로 초기화되었습니다!")
        print(f"🔧 연결된 도구 개수: {len(self.tools)}")
        
    async def chat(self, user_input: str) -> str:
        """사용자와 채팅"""
        try:
            # 에이전트 실행
            response = await self.agent.ainvoke({
                'messages': [HumanMessage(content=user_input)]
            })
            
            # 응답에서 AI 메시지 추출
            if response and 'messages' in response:
                ai_messages = [msg for msg in response['messages'] if hasattr(msg, 'content') and msg.type == 'ai']
                if ai_messages:
                    return ai_messages[-1].content
            
            return "응답을 생성할 수 없습니다."
            
        except Exception as e:
            error_msg = f"채팅 중 오류가 발생했습니다: {e}"
            print(f"❌ {error_msg}")
            return error_msg
    
    async def close(self):
        """클라이언트 종료"""
        if self.client:
            # MultiServerMCPClient는 close() 메서드가 없을 수 있음
            if hasattr(self.client, 'close'):
                try:
                    await self.client.close()
                except Exception as e:
                    print(f"⚠️ 클라이언트 종료 중 오류: {e}")
            print("🔴 MCP 클라이언트가 종료되었습니다.")

async def main():
    """메인 실행 함수"""
    agent = MCPMemoryAgent()
    
    try:
        # 에이전트 초기화
        await agent.initialize()
        
        print("\n" + "="*60)
        print("🤖 지능적 메모리 AI 어시스턴트에 오신 것을 환영합니다!")
        print("💾 모든 대화가 지식 그래프로 저장되어 기억됩니다.")
        print("📝 '/quit'으로 종료할 수 있습니다.")
        print("="*60 + "\n")
        
        # 메모리 로드 및 초기 인사
        initial_response = await agent.chat("안녕하세요! 기억을 떠올리는 중입니다...")
        print(f"🤖 AI: {initial_response}\n")
        
        # 대화 루프
        while True:
            try:
                user_input = input("👤 사용자: ").strip()
                
                if not user_input:
                    continue
                
                # 종료 명령어 처리
                if user_input.lower() in ['/quit', 'quit', '종료']:
                    print("👋 대화를 종료합니다.")
                    break
                
                # 일반 대화
                response = await agent.chat(user_input)
                print(f"🤖 AI: {response}\n")
                    
            except KeyboardInterrupt:
                print("\n👋 Ctrl+C로 종료합니다.")
                break
            except EOFError:
                print("\n👋 입력 종료로 대화를 마칩니다.")
                break
            except Exception as e:
                print(f"❌ 오류: {e}\n")
                
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
    finally:
        # 클라이언트 정리
        await agent.close()

if __name__ == "__main__":
    # 메인 실행
    asyncio.run(main()) 