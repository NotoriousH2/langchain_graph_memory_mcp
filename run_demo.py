#!/usr/bin/env python3
"""
MCP 메모리 시스템 간단 데모
서버를 별도로 실행한 후 클라이언트 테스트
"""

import asyncio
import os
from mcp_client import MCPMemoryAgent
from dotenv import load_dotenv

async def simple_demo():
    """간단한 데모 실행"""
    print("🎬 MCP 지식 그래프 메모리 시스템 데모를 시작합니다!\n")
    
    # API 키 확인
    load_dotenv('env', override=True)
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        print("💡 env 파일에 API 키를 설정해주세요.")
        return
    
    print("⚠️  주의: 먼저 memory_server.py를 별도 터미널에서 실행해주세요!")
    print("     python memory_server.py")
    input("서버가 실행되면 Enter를 눌러주세요...")
    
    agent = MCPMemoryAgent()
    
    try:
        # 에이전트 초기화
        print("🔧 에이전트 초기화 중...")
        await agent.initialize()
        print("✅ 초기화 완료!\n")
        
        # 데모 시나리오
        demo_scenarios = [
            "안녕하세요! 저는 김철수이고 삼성에서 AI 개발자로 일하고 있습니다.",
            "제 동료 이영희는 LG에서 데이터 사이언티스트로 일해요. 같은 대학 출신입니다.",
            "제가 Python을 좋아한다는 것도 기억해주세요.",
            "AI 관련된 사람들을 검색해주세요.",
        ]
        
        # 각 시나리오 실행
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"📋 시나리오 {i}")
            print(f"{'='*60}")
            
            print(f"👤 사용자: {scenario}")
            
            # AI 응답 받기
            response = await agent.chat(scenario)
            print(f"🤖 AI: {response}")
            
            # 잠시 대기
            await asyncio.sleep(1)
        
        print(f"\n{'='*60}")
        print("🎉 데모가 완료되었습니다!")
        print("💾 모든 정보가 memory.json 파일에 저장되었습니다.")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ 데모 실행 중 오류: {e}")
    finally:
        # 에이전트 정리
        await agent.close()

if __name__ == "__main__":
    asyncio.run(simple_demo()) 