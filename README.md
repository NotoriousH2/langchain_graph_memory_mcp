# 🧠 MCP 지식 그래프 메모리 시스템

**올바른 FastMCP와 LangGraph ReAct Agent 구현**

AI가 대화 간에 정보를 기억하고 연결할 수 있는 지식 그래프 기반의 지속적 메모리 시스템입니다.

## ✨ 주요 기능

### 🎯 핵심 개념
- **📝 Entities (엔티티)**: 사람, 조직, 개념 등의 노드
- **🔗 Relations (관계)**: 엔티티 간의 방향성 연결  
- **👁️ Observations (관찰사항)**: 엔티티에 대한 개별적인 정보

### 🛠️ 제공되는 도구들
- `create_entities` - 새로운 엔티티 생성
- `create_relations` - 엔티티 간 관계 설정
- `add_observations` - 관찰사항 추가
- `search_nodes` - 검색 기능
- `read_graph` - 전체 지식 그래프 조회

## 🚀 설치 및 설정

### 1. 필요한 패키지 설치
```bash
pip install mcp langchain-mcp-adapters langgraph langchain-openai python-dotenv
```

### 2. 환경 변수 설정
`env` 파일에 OpenAI API 키를 설정하세요:
```
OPENAI_API_KEY="your-openai-api-key-here"
```

## 📖 사용법

### 🖥️ 1단계: 서버 실행
**터미널 1에서:**
```bash
python memory_server.py
```
서버가 포트 8084에서 실행됩니다.

### 🤖 2단계: 클라이언트 실행
**터미널 2에서:**
```bash
python mcp_client.py
```

### 🎮 3단계: 데모 실행 (선택사항)
```bash
python run_demo.py
```

## 💬 대화 예시

```
👤 사용자: 안녕하세요! 저는 김철수이고 삼성에서 AI 개발자로 일하고 있어요.

🤖 AI: 안녕하세요 김철수님! 반갑습니다. 정보를 메모리에 저장하겠습니다.
      [메모리 도구 사용하여 엔티티와 관계 생성]

👤 사용자: 제 동료 이영희는 LG에서 데이터 사이언티스트로 일해요.

🤖 AI: 이영희님에 대한 정보도 저장했습니다!
      김철수님과의 동료 관계도 기록했습니다.
```

## 🏗️ 아키텍처

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   mcp_client.py     │    │  memory_server.py   │    │   memory.json   │
│                     │    │                     │    │                 │
│ LangGraph           │◄──►│ FastMCP             │◄──►│ 지식 그래프     │
│ ReAct Agent         │    │ streamable-http     │    │ 저장소          │
│ MultiServerClient   │    │ 포트 8084           │    │                 │
└─────────────────────┘    └─────────────────────┘    └─────────────────┘
```

## 📁 파일 구조

```
.
├── memory_server.py      # MCP 서버 (FastMCP)
├── mcp_client.py        # MCP 클라이언트 (LangGraph Agent)
├── run_demo.py          # 간단한 데모
├── env                  # 환경 변수 (API 키)
├── memory.json          # 지식 그래프 저장소 (자동 생성)
└── README.md           # 이 파일
```

## 🔧 기술 스택

- **MCP 서버**: `mcp.server.fastmcp.FastMCP`
- **전송 방식**: `streamable-http` (HTTP/SSE)
- **클라이언트**: `langchain_mcp_adapters.client.MultiServerMCPClient`
- **에이전트**: `langgraph.prebuilt.create_react_agent`
- **LLM**: `langchain_openai.ChatOpenAI` (gpt-4o-mini)

## 📊 데이터 구조 예시

### Entity (엔티티)
```json
{
  "name": "김철수",
  "entityType": "person", 
  "observations": ["AI 개발자", "Python 선호"]
}
```

### Relation (관계)
```json
{
  "from_entity": "김철수",
  "to_entity": "삼성",
  "relationType": "works_at"
}
```

## ⚠️ 주의사항

1. **서버 먼저 실행**: 클라이언트 실행 전에 반드시 서버를 먼저 실행하세요
 2. **포트 충돌**: 8084 포트가 사용 중이면 `memory_server.py`에서 포트 번호를 변경하세요
3. **API 키**: OpenAI API 키가 필요합니다
4. **패키지 버전**: 최신 버전의 MCP 관련 패키지를 사용하세요

## 🔧 문제 해결

### 서버 연결 오류
```
❌ Connection refused
```
→ `memory_server.py`가 실행 중인지 확인하세요

### API 키 오류  
```
❌ OPENAI_API_KEY가 설정되지 않았습니다
```
→ `env` 파일의 API 키를 확인하세요

### 패키지 오류
```
❌ ModuleNotFoundError: No module named 'mcp'
```
→ `pip install mcp langchain-mcp-adapters` 실행하세요

## 🎯 활용 시나리오

1. **개인 비서**: 사용자 정보와 선호도 기억
2. **프로젝트 관리**: 팀원과 역할 관계 추적
3. **학습 도우미**: 개념들 간의 관계 정리
4. **네트워킹**: 인맥 관리 및 연결점 발견

---

🎉 **올바른 MCP 구현으로 지능적 메모리를 경험해보세요!** 🎉 