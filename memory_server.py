#!/usr/bin/env python3
"""
MCP 메모리 서버 - 올바른 FastMCP 구현
지식 그래프 기반의 지속적 메모리 시스템
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('env', override=True)

@dataclass
class Entity:
    """엔티티: 지식 그래프의 노드"""
    name: str
    entityType: str
    observations: List[str]

@dataclass
class Relation:
    """관계: 엔티티 간의 방향성 연결"""
    from_entity: str
    to_entity: str
    relationType: str

class MemoryGraph:
    """지식 그래프 메모리 시스템"""
    
    def __init__(self, storage_path: str = "memory.json"):
        self.storage_path = storage_path
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.load_from_file()
    
    def load_from_file(self):
        """파일에서 메모리 로드"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 엔티티 로드
                for entity_data in data.get('entities', []):
                    entity = Entity(**entity_data)
                    self.entities[entity.name] = entity
                
                # 관계 로드
                for relation_data in data.get('relations', []):
                    relation = Relation(**relation_data)
                    self.relations.append(relation)
                    
            except Exception as e:
                print(f"메모리 로드 실패: {e}")
    
    def save_to_file(self):
        """파일에 메모리 저장"""
        try:
            data = {
                'entities': [asdict(entity) for entity in self.entities.values()],
                'relations': [asdict(relation) for relation in self.relations]
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"메모리 저장 실패: {e}")
    
    def create_entities(self, entities_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """새로운 엔티티들 생성"""
        created = []
        for entity_data in entities_data:
            name = entity_data['name']
            if name not in self.entities:
                entity = Entity(
                    name=name,
                    entityType=entity_data['entityType'],
                    observations=entity_data.get('observations', [])
                )
                self.entities[name] = entity
                created.append(name)
        
        self.save_to_file()
        return {"created_entities": created}
    
    def create_relations(self, relations_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """새로운 관계들 생성"""
        created = []
        for relation_data in relations_data:
            from_entity = relation_data['from']
            to_entity = relation_data['to']
            relation_type = relation_data['relationType']
            
            # 중복 관계 확인
            exists = any(
                r.from_entity == from_entity and 
                r.to_entity == to_entity and 
                r.relationType == relation_type
                for r in self.relations
            )
            
            if not exists:
                relation = Relation(from_entity, to_entity, relation_type)
                self.relations.append(relation)
                created.append(f"{from_entity} -> {relation_type} -> {to_entity}")
        
        self.save_to_file()
        return {"created_relations": created}
    
    def add_observations(self, observations_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """기존 엔티티에 관찰사항 추가"""
        added = {}
        for obs_data in observations_data:
            entity_name = obs_data['entityName']
            contents = obs_data['contents']
            
            if entity_name in self.entities:
                entity = self.entities[entity_name]
                new_observations = []
                for content in contents:
                    if content not in entity.observations:
                        entity.observations.append(content)
                        new_observations.append(content)
                added[entity_name] = new_observations
            else:
                added[entity_name] = f"엔티티 '{entity_name}'를 찾을 수 없습니다"
        
        self.save_to_file()
        return {"added_observations": added}
    
    def search_nodes(self, query: str) -> Dict[str, Any]:
        """노드 검색 (엔티티 이름, 타입, 관찰사항에서 검색)"""
        query_lower = query.lower()
        matched_entities = []
        related_relations = []
        
        for entity in self.entities.values():
            # 엔티티 이름, 타입, 관찰사항에서 검색
            if (query_lower in entity.name.lower() or 
                query_lower in entity.entityType.lower() or
                any(query_lower in obs.lower() for obs in entity.observations)):
                
                matched_entities.append(asdict(entity))
                
                # 관련 관계들 찾기
                for relation in self.relations:
                    if (relation.from_entity == entity.name or 
                        relation.to_entity == entity.name):
                        if asdict(relation) not in related_relations:
                            related_relations.append(asdict(relation))
        
        return {
            "query": query,
            "matched_entities": matched_entities,
            "related_relations": related_relations,
            "total_matches": len(matched_entities)
        }
    
    def read_graph(self) -> Dict[str, Any]:
        """전체 지식 그래프 조회"""
        return {
            "entities": [asdict(entity) for entity in self.entities.values()],
            "relations": [asdict(relation) for relation in self.relations],
            "summary": {
                "total_entities": len(self.entities),
                "total_relations": len(self.relations)
            }
        }

# FastMCP 서버 초기화 (포트 8084 사용)
mcp = FastMCP(
    name="memory_knowledge_graph",
    instructions="지식 그래프 기반 메모리 시스템 - 엔티티, 관계, 관찰사항을 관리합니다.",
    port=8084
)

# 메모리 그래프 인스턴스
memory_graph = MemoryGraph()

@mcp.resource("memory://current_status")
def current_memory_status() -> str:
    """현재 메모리 상태 정보를 제공합니다."""
    from datetime import datetime
    stats = memory_graph.read_graph()
    return f"""
현재 시간: {datetime.now().isoformat()}
저장된 엔티티: {stats['summary']['total_entities']}개
저장된 관계: {stats['summary']['total_relations']}개
메모리 파일: {memory_graph.storage_path}
"""

@mcp.tool()
def create_entities(entities: List[Dict[str, Any]]) -> str:
    """
    새로운 엔티티들을 지식 그래프에 생성합니다.
    
    Args:
        entities: 생성할 엔티티들의 리스트
                 각 엔티티는 name, entityType, observations 필드를 가집니다.
    
    Returns:
        생성된 엔티티들의 정보
    """
    result = memory_graph.create_entities(entities)
    return f"✅ 생성된 엔티티: {', '.join(result['created_entities'])}"

@mcp.tool()
def create_relations(relations: List[Dict[str, str]]) -> str:
    """
    엔티티들 간의 새로운 관계들을 생성합니다.
    
    Args:
        relations: 생성할 관계들의 리스트
                  각 관계는 from, to, relationType 필드를 가집니다.
    
    Returns:
        생성된 관계들의 정보
    """
    result = memory_graph.create_relations(relations)
    return f"🔗 생성된 관계:\n" + "\n".join(result['created_relations'])

@mcp.tool()
def add_observations(observations: List[Dict[str, Any]]) -> str:
    """
    기존 엔티티에 새로운 관찰사항들을 추가합니다.
    
    Args:
        observations: 추가할 관찰사항들의 리스트
                     각 항목은 entityName과 contents 필드를 가집니다.
    
    Returns:
        추가된 관찰사항들의 정보
    """
    result = memory_graph.add_observations(observations)
    response = "👁️ 추가된 관찰사항:\n"
    for entity_name, obs_list in result['added_observations'].items():
        if isinstance(obs_list, list):
            response += f"- {entity_name}: {', '.join(obs_list)}\n"
        else:
            response += f"- {entity_name}: {obs_list}\n"
    return response

@mcp.tool()
def search_nodes(query: str) -> str:
    """
    지식 그래프에서 노드를 검색합니다.
    엔티티 이름, 타입, 관찰사항 내용에서 검색합니다.
    
    Args:
        query: 검색할 쿼리 문자열
    
    Returns:
        일치하는 엔티티들과 관련 관계들의 정보
    """
    result = memory_graph.search_nodes(query)
    
    if result['total_matches'] == 0:
        return f"🔍 '{query}' 검색 결과가 없습니다."
    
    response = f"🔍 '{query}' 검색 결과 ({result['total_matches']}개):\n\n"
    
    for entity in result['matched_entities']:
        response += f"📝 {entity['name']} ({entity['entityType']})\n"
        response += f"   관찰사항: {', '.join(entity['observations'])}\n\n"
    
    if result['related_relations']:
        response += "🔗 관련 관계들:\n"
        for relation in result['related_relations']:
            response += f"   {relation['from_entity']} → {relation['relationType']} → {relation['to_entity']}\n"
    
    return response

@mcp.tool()
def read_graph() -> str:
    """
    전체 지식 그래프의 구조를 조회합니다.
    
    Returns:
        모든 엔티티와 관계, 요약 정보를 포함한 지식 그래프
    """
    result = memory_graph.read_graph()
    
    response = f"🧠 전체 메모리 그래프 (엔티티: {result['summary']['total_entities']}개, 관계: {result['summary']['total_relations']}개)\n\n"
    
    # 엔티티들
    if result['entities']:
        response += "📝 엔티티들:\n"
        for entity in result['entities']:
            response += f"  • {entity['name']} ({entity['entityType']})\n"
            if entity['observations']:
                response += f"    관찰사항: {', '.join(entity['observations'])}\n"
        response += "\n"
    
    # 관계들
    if result['relations']:
        response += "🔗 관계들:\n"
        for relation in result['relations']:
            response += f"  • {relation['from_entity']} → {relation['relationType']} → {relation['to_entity']}\n"
    
    return response

if __name__ == "__main__":
    # 서버 실행 (streamable-http 방식)
    mcp.run(transport="streamable-http") 