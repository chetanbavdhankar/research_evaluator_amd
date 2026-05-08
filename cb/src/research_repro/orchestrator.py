from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
from datetime import datetime
from pathlib import Path
import re

from research_repro.schemas.pipeline_state import PipelineState, PhaseStatus
from research_repro.config import AppConfig
from research_repro.phases.phase1_paper_comprehension import executor as phase1
from research_repro.phases.phase2_data_sourcing import executor as phase2
from research_repro.phases.phase3_environment import executor as phase3
from research_repro.phases.phase4_data_processing import executor as phase4
from research_repro.phases.phase5_analysis_execution import executor as phase5
from research_repro.phases.phase6_results_validation import executor as phase6

# The state dictionary for LangGraph, which maps directly to PipelineState
class GraphState(TypedDict):
    state: PipelineState
    config: AppConfig

def create_phase_stub(phase_num: int, phase_name: str):
    def stub_node(data: GraphState) -> GraphState:
        state = data["state"]
        # Stub implementation: immediately block
        status = PhaseStatus(
            phase_number=phase_num,
            phase_name=phase_name,
            status="blocked",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            flags_raised=["Not implemented"]
        )
        
        # Replace the old status if it exists, else append
        idx = next((i for i, p in enumerate(state.phase_statuses) if p.phase_number == phase_num), -1)
        if idx >= 0:
            state.phase_statuses[idx] = status
        else:
            state.phase_statuses.append(status)
            
        return {"state": state, "config": data["config"]}
    return stub_node

def phase1_node(data: GraphState) -> GraphState:
    state = data["state"]
    config = data["config"]
    
    status = PhaseStatus(
        phase_number=1,
        phase_name="paper_comprehension",
        status="in_progress",
        started_at=datetime.utcnow()
    )
    # Update state
    idx = next((i for i, p in enumerate(state.phase_statuses) if p.phase_number == 1), -1)
    if idx >= 0:
        state.phase_statuses[idx] = status
    else:
        state.phase_statuses.append(status)
        
    result = phase1.run(state.paper_input, Path(state.run_directory), config)
    
    status.status = result.status
    status.completed_at = datetime.utcnow()
    status.output_path = result.artifact_path
    status.flags_raised = result.flags_raised
    
    if result.status == "complete":
        state.paper_knowledge_artifact = result.artifact_path
        
    # Re-update
    state.phase_statuses[idx if idx >= 0 else len(state.phase_statuses)-1] = status
    
    return {"state": state, "config": config}

def phase2_node(data: GraphState) -> GraphState:
    state = data["state"]
    config = data["config"]
    
    status = PhaseStatus(
        phase_number=2,
        phase_name="data_sourcing",
        status="in_progress",
        started_at=datetime.utcnow()
    )
    idx = next((i for i, p in enumerate(state.phase_statuses) if p.phase_number == 2), -1)
    if idx >= 0:
        state.phase_statuses[idx] = status
    else:
        state.phase_statuses.append(status)
        
    result = phase2.run(state.paper_knowledge_artifact, Path(state.run_directory), config)
    
    status.status = result.status
    status.completed_at = datetime.utcnow()
    status.output_path = result.artifact_path
    status.flags_raised = result.flags_raised
    
    if result.status in ["complete", "all_acquired", "partial"]:
        state.data_manifest = result.artifact_path
        
    state.phase_statuses[idx if idx >= 0 else len(state.phase_statuses)-1] = status
    
    return {"state": state, "config": config}

def phase3_node(data: GraphState) -> GraphState:
    state = data["state"]
    config = data["config"]
    
    status = PhaseStatus(
        phase_number=3,
        phase_name="environment_reconstruction",
        status="in_progress",
        started_at=datetime.utcnow()
    )
    idx = next((i for i, p in enumerate(state.phase_statuses) if p.phase_number == 3), -1)
    if idx >= 0:
        state.phase_statuses[idx] = status
    else:
        state.phase_statuses.append(status)
        
    result = phase3.run(state.paper_knowledge_artifact, Path(state.run_directory), config)
    
    status.status = result.status
    status.completed_at = datetime.utcnow()
    status.output_path = result.artifact_path
    status.flags_raised = result.flags_raised
    
    if result.status in ["complete", "partial"]:
        state.environment_spec = result.artifact_path
        
    state.phase_statuses[idx if idx >= 0 else len(state.phase_statuses)-1] = status
    
    return {"state": state, "config": config}

def phase4_node(data: GraphState) -> GraphState:
    state = data["state"]
    config = data["config"]
    
    status = PhaseStatus(
        phase_number=4,
        phase_name="data_processing",
        status="in_progress",
        started_at=datetime.utcnow()
    )
    idx = next((i for i, p in enumerate(state.phase_statuses) if p.phase_number == 4), -1)
    if idx >= 0:
        state.phase_statuses[idx] = status
    else:
        state.phase_statuses.append(status)
        
    result = phase4.run(state.paper_knowledge_artifact, state.data_manifest, state.environment_spec, Path(state.run_directory), config)
    
    status.status = result.status
    status.completed_at = datetime.utcnow()
    status.output_path = result.artifact_path
    status.flags_raised = result.flags_raised
    
    if result.status == "complete":
        state.processed_dataset = result.artifact_path
        
    state.phase_statuses[idx if idx >= 0 else len(state.phase_statuses)-1] = status
    
    return {"state": state, "config": config}

def phase5_node(data: GraphState) -> GraphState:
    state = data["state"]
    config = data["config"]
    
    status = PhaseStatus(
        phase_number=5,
        phase_name="analysis_execution",
        status="in_progress",
        started_at=datetime.utcnow()
    )
    idx = next((i for i, p in enumerate(state.phase_statuses) if p.phase_number == 5), -1)
    if idx >= 0:
        state.phase_statuses[idx] = status
    else:
        state.phase_statuses.append(status)
        
    result = phase5.run(state.paper_knowledge_artifact, state.processed_dataset, state.environment_spec, Path(state.run_directory), config)
    
    status.status = result.status
    status.completed_at = datetime.utcnow()
    status.output_path = result.artifact_path
    status.flags_raised = result.flags_raised
    
    if result.status == "complete":
        state.analysis_results = result.artifact_path
        
    state.phase_statuses[idx if idx >= 0 else len(state.phase_statuses)-1] = status
    
    return {"state": state, "config": config}

def phase6_node(data: GraphState) -> GraphState:
    state = data["state"]
    config = data["config"]
    
    status = PhaseStatus(
        phase_number=6,
        phase_name="results_validation",
        status="in_progress",
        started_at=datetime.utcnow()
    )
    idx = next((i for i, p in enumerate(state.phase_statuses) if p.phase_number == 6), -1)
    if idx >= 0:
        state.phase_statuses[idx] = status
    else:
        state.phase_statuses.append(status)
        
    result = phase6.run(state.paper_knowledge_artifact, state.analysis_results, Path(state.run_directory), config)
    
    status.status = result.status
    status.completed_at = datetime.utcnow()
    status.output_path = result.artifact_path
    status.flags_raised = result.flags_raised
    
    if result.status == "complete":
        state.reproducibility_report = result.artifact_path
        state.overall_status = "completed"
        
    state.phase_statuses[idx if idx >= 0 else len(state.phase_statuses)-1] = status
    
    return {"state": state, "config": config}

def partial_report_node(data: GraphState) -> GraphState:
    state = data["state"]
    state.overall_status = "terminated"
    # Write the pipeline state
    state_path = Path(state.run_directory) / "pipeline_state.json"
    with open(state_path, "w") as f:
        f.write(state.model_dump_json(indent=2))
    return {"state": state, "config": data["config"]}

def check_phase1_status(data: GraphState) -> str:
    state = data["state"]
    p1 = next((p for p in state.phase_statuses if p.phase_number == 1), None)
    if p1 and p1.status == "complete":
        return "phase2"
    return "partial_report"

def check_phase_status(phase_num: int):
    def checker(data: GraphState) -> str:
        state = data["state"]
        p = next((p for p in state.phase_statuses if p.phase_number == phase_num), None)
        if p and p.status in ["complete", "all_acquired"]:
            return f"phase{phase_num+1}"
        return "partial_report"
    return checker

def build_orchestrator():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("phase1", phase1_node)
    workflow.add_node("phase2", phase2_node)
    workflow.add_node("phase3", phase3_node)
    workflow.add_node("phase4", phase4_node)
    workflow.add_node("phase5", phase5_node)
    workflow.add_node("phase6", phase6_node)
    workflow.add_node("partial_report", partial_report_node)
    
    workflow.set_entry_point("phase1")
    
    workflow.add_conditional_edges("phase1", check_phase1_status, {"phase2": "phase2", "partial_report": "partial_report"})
    workflow.add_conditional_edges("phase2", check_phase_status(2), {"phase3": "phase3", "partial_report": "partial_report"})
    workflow.add_conditional_edges("phase3", check_phase_status(3), {"phase4": "phase4", "partial_report": "partial_report"})
    workflow.add_conditional_edges("phase4", check_phase_status(4), {"phase5": "phase5", "partial_report": "partial_report"})
    workflow.add_conditional_edges("phase5", check_phase_status(5), {"phase6": "phase6", "partial_report": "partial_report"})
    
    # Phase 6 goes to END on success or partial_report on fail
    workflow.add_conditional_edges("phase6", check_phase_status(6), {"phase7": END, "partial_report": "partial_report"})
    workflow.add_edge("partial_report", END)
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
